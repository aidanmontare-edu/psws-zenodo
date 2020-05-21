#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uploads to Zenodo via the REST API
"""

__version__ = "0.1.0"

from pathlib import Path
import sys
import hashlib
import json
import requests
import argparse
import webbrowser
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from datetime import datetime, timezone

def read_access_token():
    """Reads the access token from `secrets.json` file."""
    try:
        # We store our various secrets in an aptly named file
        with open('config/secrets.json', 'r') as data_file:
            return json.load(data_file)['access_token']
    except FileNotFoundError:
        raise Exception("You must either provide an access token"
                        " on the commnad line or in the file"
                        " `config/secrets.json`")
        
def read_local_path():
    """
    Reads the local path from `secrets.json` file.
    
    Todo elimitate repeated code
    """
    try:
        # We store our various secrets in an aptly named file
        with open('config/secrets.json', 'r') as data_file:
            return json.load(data_file)['local_path']
    except FileNotFoundError:
        raise Exception("You must either provide a local path"
                        " on the commnad line or in the file"
                        " `config/secrets.json`")


parser = argparse.ArgumentParser(
    description="Upload the given file(s) to Zenodo via the REST API."
                " In development, so arguments and behavior my vary.")
parser.add_argument('--path',
                    default=read_local_path(),
                    help="The file(s) to include in the upload. If no path is"
                    " specified, the path stored in the file `config/secrets.json`
                    " is used ")
# parser.add_argument('-m', '--metadata-file',
#                     help="JSON file containing metadata for the upload.")
parser.add_argument('-t', '--token', default=read_access_token(),
                    help="Access token for the Zenodo account you wish"
                    " to upload to. If no token is specified, the token"
                    " stored in the file `config/secrets.json` is used.")
parser.add_argument('-c', '--check', action='store_true',
                    help="Check if the file(s) at <path> are"
                    " already uploaded to your Zenodo account,"
                    " but don't make any changes.")
parser.add_argument('-w', '--watch', action='store_true',
                    help="Instead of running once, run continuously"
                    " and watch for changes to the file(s) at the"
                    " specified path(s). An upload will be triggered"
                    " anytime a change is detected")
# parser.add_argument('-d', '--daemon',
#                     help="Daemon mode. Runs in the background,"
#                     " and checks once per day which files have"
#                     " not been uploaded to Zenodo. Those files"
#                     " are then added to the appropriate upload.")
parser.add_argument('-s', '--sandbox', action='store_true',
                    help="Use sandbox.zenodo.org instead of"
                    " zenodo.org. You will need to create an account on the"
                    " sandbox server, and an access token for that account,"
                    " if you do not already have these.")
parser.add_argument('-V', '--version', action='store_true',
                    dest='version',
                    help="Show the version number and exit.")
# parser.add_argument('--show-urls', action='store_true',
#                     help="Whenever the program output mentions a Zenodo"
#                     " file or upload, also output a URL to it.")

args = parser.parse_args()

if args.version:
    print(__version__)
    sys.exit()

if args.token=="":
    None

if args.sandbox:
    url = "https://sandbox.zenodo.org/api/deposit/depositions"
else:
    url = "https://zenodo.org/api/deposit/depositions"

# read current-target.json
try:
    with open('config/current-target.json', 'r') as data_file:
        target = json.load(data_file)
except FileNotFoundError:
    raise Exception("You must provide a target in the file"
                    " `config/current-target.json`")
        
print("Target id:", target["id"])

if args.sandbox != target["onZenodoSandboxServer"]:
    raise Exception("The target" +
                    (" is" if target["onZenodoSandboxServer"] else " is not") +
                    " specified on the sandbox server, but -s/--sandbox" +
                    (" was" if args.sandbox else " was not") +
                    " passed.\nPlease change either the target or the" +
                    " command line arguments.")

target_url = url + "/" + str(target["id"])

if not Path(args.path).exists():
    raise Exception("The local path does not"
                    " exist on the system. This is likely"
                    " an error.")

def makeRequest(kind, url, params=None, **kwargs):
    """
    Makes an http request of the specified kind, and does
    a bunch of other useful things

    Parameters
    ----------
    kind : TYPE
        DESCRIPTION.
    url : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if params is None:
        params = {}
    
    params["access_token"] = args.token
    
    print(kwargs)
    
    response = getattr(requests, kind)(url, params=params, **kwargs)
    
    print(response.url)
    
    # raise exceptions if an unsuccessful HTTP code is returned
    response.raise_for_status()
    
    return response

def compareToTargetURL():
    """
    Checks the local directory against the zenodo target_url.

    Raises
    ------
    Exception
        When there is already an unpublished draft of this resource.

    Returns
    -------
    to_be_updated : TYPE
        DESCRIPTION.
    to_be_uploaded : TYPE
        DESCRIPTION.

    """
    
    global target_url
    
    # get the most recent version of the target
    r = requests.get(target_url, params={'access_token': args.token})
    # r = makeRequest("get", target_url)
    
    if "latest_draft" in r.json()["links"]:
        # target_url = r.json()["links"]["latest_draft"]
        # there is already a new draft for this deposition
        # the API will not allow more than one draft at a time,
        # and this situation is likely unsafe anyway
        raise Exception("The deposition already has an unpublished draft."
                        " Please deal with this on the Zenodo website:\n" +
                        r.json()["links"]["latest_draft_html"])
    else:
        latest_target_id = r.json()["links"]["latest"].rsplit("/", 1)[-1]
        target_url = url + "/" + str(latest_target_id)
    
    # get files for deposition
    request = requests.get(target_url + "/files",
                           params={'access_token': args.token})
    # request = makeRequest("get", target_url + "/files")
    
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    
    # get the files in the current directory that do not
    # start with '.'
    local_files = [path for path in Path(args.path).glob("*")
                 if path.is_file() and path.name[0] != '.']
    
    print(local_files)
    
    # find the checksums of all the files
    checksums = {}
    
    for file in local_files:
        if not file.exists():
            raise Exception(file.name, "does not exist")
        
        md5 = hashlib.md5()
        
        with open(file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        
        checksums[file] = md5.hexdigest()
        
        #print(file.name + " " + md5.hexdigest())
        
    # see which files are in the upload
    # find the files that are not uploaded
    to_be_updated = []
    to_be_uploaded = []
    
    for local_file in local_files:
        matchedExact = False
        matched = False
        
        for zenodo_file in request.json():
            if local_file.name.replace(" ", "_") == zenodo_file["filename"]:
                matched = True
                
                if checksums[local_file] == zenodo_file["checksum"]:
                    #print("Match! local_file: {0}, zenodo_file: {1}".format(local_file.name, zenodo_file["filename"]))
                    matchedExact = True
                else:
                    None
                    #print("No match. local_file: {0}, zenodo_file: {1}".format(local_file.name, zenodo_file["filename"]))
        
        if matchedExact:
            print(local_file.name, "is uploaded in current form.")
        elif matched:
            print(local_file.name, "needs updating.")
            to_be_updated.append(local_file)
            to_be_uploaded.append(local_file)
        else:
            print(local_file.name, "has not been uploaded")
            to_be_uploaded.append(local_file)
            
    return to_be_updated, to_be_uploaded


def do():
    """Just do it!"""
    
    to_be_updated, to_be_uploaded = compareToTargetURL()
    
    if len(to_be_uploaded) == 0:
        print("Nothing to upload.")
        return
    
    # create a new version of the deposition so that we can add files
    r = requests.post(target_url + "/actions/newversion",
                      params={'access_token': args.token})
    # r = makeRequest("post", target_url + "/actions/newversion")
    
    # get the new version
    new_target_url = r.json()["links"]["latest_draft"]
    
    request = requests.get(new_target_url + "/files",
                           params={'access_token': args.token})
    
    # delete deposition files for the files that will be updated
    for file in to_be_updated:
        for zenodo_file in request.json():
            if file.name.replace(" ", "_") == zenodo_file["filename"]:
                r = requests.delete(zenodo_file["links"]["self"],
                                    params={'access_token': args.token})
                print("Deleted deposition file with status code", r.status_code)
                break
    
    # upload the not-yet-uploaded files
    for file in to_be_uploaded:
        print("Uploading", file.name)
        # create deposition file (upload a file)
        r_df = requests.post(new_target_url + "/files",
                             data={'name': file.name},
                             files={'file': file.read_bytes()},
                             params={'access_token': args.token})
        # r_df = makeRequest("post",
        #                    new_target_url + "/files",
        #                    data={'name': file.name},
        #                    files={'file': file.read_bytes()})
        
        print("Sent file with status code", r_df.status_code)
        
        if r_df.status_code==400:
            print(r_df.json())
    
    now = datetime.now(timezone.utc)
    # update the date on the deposition
    r = requests.put(new_target_url,
                     data={"metadata": {"publication_date": now.isoformat()}})
    print("Changed time with status code", r.status_code)
    
    if r.status_code == 401:
        print(r.json())
    
    # publish the new deposiiton version
    r = requests.post(new_target_url + "/actions/publish",
                      params={'access_token': args.token})
    # r = makeRequest("post", new_target_url + "/actions/publish")
    
    print("Published deposition with status code", r.status_code)
    
    if r.status_code==400:
        print(r.json())

# description_file = "C:\\Users\\aidan\\Documents\\W8EDU\\psws-zenodo\\test-files\\Readme_5_Mhz Cleveland Heights.txt"
# description_text = ""
# with open(description_file, 'r') as f:
#     description_text = f.read()

# # create deposition

# data = {
#     "metadata": {
#         "title": "target for WWV 5MHz Frequency Measurements from Cleveland, OH, USA",
#         "upload_type": "dataset",
#         "description": description_text,
#         "creators": [
#             {"name": "Kazdan, David", "affiliation": "Case Western Reserve University"}
#         ],
#         "keywords": ["wwv"],
#         "communities": [{"identifier": "hamsci-test"}],
#         "locations": [
#             {
#                 "lat": 41.493744,
#                 "lon": -81.578039,
#                 "place": "location where recordings are made"
#             }
#         ]
#     }
# }

# headers = {"Content-Type": "application/json"}

# r = requests.post(url, data=json.dumps(data), headers=headers,
#                  params={'access_token': args.token})

# print("Created upload with status code", r.status_code)

# # create deposition file (upload a file)

# file_name = os.path.basename(args.path)

# data = {'name': file_name}
# files = {'file': open(args.path, 'rb')}
# r_df = requests.post(r.json()['links']['files'], data=data, files=files,
#                   params={'access_token': args.token})

# print("Sent file with status code", r_df.status_code)

# # publish deposition

# r_p = requests.post(r.json()['links']['publish'],
#                     params={'access_token': args.token})

# print("Published upload with status code", r_p.status_code)
# print()
# print("Response:")
# print(json.dumps(r_p.json(), indent=2))

# webbrowser.open(r_p.json()['links']['record_html'])


def getAllDepositionsOfUser():
    """Get all the depositions of the user thus far, and return
    a simplified list of deposition objects"""
        
    page = 1 # page of the depositions list we are looking at
    cache = []
    
    while True:
        request = requests.get(url,
                               params={'access_token': args.token, 'page': page})
        
        if request.status_code != 200:
            print("API fail with status code", request.status_code)
            break
        
        if not request.json():
            break
        
        for deposition in request.json():
            cache.append({"id": deposition["id"]})
            if deposition["submitted"]:
                cache[len(cache) - 1]["submitted"] = True
                cache[len(cache) - 1]["link"] = deposition["links"]["record_html"]
            else:
                cache[len(cache) - 1]["submitted"] = False
                cache[len(cache) - 1]["link"] = deposition["links"]["html"]
            
            if "files" in deposition:
                cache[len(cache) - 1]["files"] = []
                for file in deposition["files"]:
                    cache[len(cache) - 1]["files"].append({"filename": file["filename"],
                                                           "checksum": file["checksum"]})
                    
        page += 1
    
    return cache




def doWrap():
    global observer
    
    observer.stop()
    do()
    observer.start()

class UploadingEventHandler(LoggingEventHandler):
    """
    Logs all the events captured, and triggers the upload process
    to start
    """

    def on_created(self, event):
        super(UploadingEventHandler, self).on_created(event)

        do()

    def on_modified(self, event):
        super(UploadingEventHandler, self).on_modified(event)

        do()


def watch():
    """Implementation of -w/--watch option."""
    
    print("Starting watchdog")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = UploadingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, args.path, recursive=True)
    observer.start()
    print("Awaiting new changes")
    try:
        while observer.isAlive():
            print("loop started")
            observer.join()
    except KeyboardInterrupt:
        print("Stopping")
        observer.stop()
    observer.join()

if args.watch:
    watch()
elif args.check:
    
    print("Comparing local to remote...")
    print("Local:", args.path)
    print("Remote:", target_url)
    
    to_be_updated, to_be_uploaded = compareToTargetURL()
    
    print()
    
    if to_be_updated:
        print("Old version will be removed:")
        for file in to_be_updated:
            print(file.name)
    else:
        print("No existing upload files to modify.")
    
    print()
    
    if to_be_uploaded:
        print("Will be uploaded:")
        for file in to_be_uploaded:
            print(file.name)
    else:
        print("No new files to upload.")
else:
    do()
