# -*- coding: utf-8 -*-
"""
Uploads to Zenodo via the REST API
"""

from pathlib import Path
import hashlib
import json
import requests
import argparse
import webbrowser
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

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

parser = argparse.ArgumentParser(
    description="Upload the given file(s) to Zenodo via the REST API."
                " Currently only works with a single file, not directories.")
parser.add_argument('--path',
                    default='C:\\Users\\aidan\\Documents\\W8EDU\\psws-zenodo\\test-files',
                    help="The file(s) to include in the upload.")
# parser.add_argument('-m', '--metadata-file',
#                     help="JSON file containing metadata for the upload.")
parser.add_argument('-t', '--token', default=read_access_token(),
                    help="Access token for the Zenodo account you wish"
                    " to upload to. If no token is specified, the token"
                    " stored in the file `config/secrets.json` is used.")
# parser.add_argument('-c', '--check',
#                     help="Check if the file(s) at <path> are"
#                     " already uploaded to your Zenodo account.")
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
# parser.add_argument('--show-urls', action='store_true',
#                     help="Whenever the program output mentions a Zenodo"
#                     " file or upload, also output a URL to it.")

args = parser.parse_args()

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

def do():
    """Just do it!"""
    global target_url
    
    # get the most recent version of the target
    r = requests.get(target_url, params={'access_token': args.token})
    
    if "latest_draft" in r.json()["links"]:
        # target_url = r.json()["links"]["latest_draft"]
        # there is already a new draft for this deposition
        # the API will not allow more than one draft at a time,
        # and this situation is likely unsafe anyway
        raise Exception("The deposition already has an unpublished draft."
                        " Please deal with this on the Zenodo website:\n" +
                        r.json()["links"]["latest_draft"])
    else:
        latest_target_id = r.json()["links"]["latest"].rsplit("/", 1)[-1]
        target_url = url + "/" + str(latest_target_id)
    
    # get files for deposition
    request = requests.get(target_url + "/files",
                           params={'access_token': args.token})
    
    if request.status_code != 200:
        print("API fail with status code", request.status_code)
        
    files = request.json()
    
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    
    # get the files in the current directory that do not
    # start with '.'
    cwd_files = [path for path in Path(args.path).glob("*")
                 if path.is_file() and path.name[0] != '.']
    
    # find the checksums of all the files
    checksums = {}
    
    for file in cwd_files:
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
    to_be_uploaded = []
    
    for local_file in cwd_files:
        matched = False
        for zenodo_file in request.json():
            if checksums[local_file] == zenodo_file["checksum"]:
                #print("Match! local_file: {0}, zenodo_file: {1}".format(local_file.name, zenodo_file["filename"]))
                matched = True
            else:
                None
                #print("No match. local_file: {0}, zenodo_file: {1}".format(local_file.name, zenodo_file["filename"]))
                
        if matched:
            print("{0} has already been uploaded.".format(local_file.name))
        else:
            print("{0} has not been uploaded.".format(local_file.name))
            to_be_uploaded.append(local_file)
    
    if len(to_be_uploaded) == 0:
        print("Nothing to upload. Goodbye!")
    
    # create a new version of the deposition so that we can add files
    r = requests.post(target_url + "/actions/newversion",
                      params={'access_token': args.token})
    
    # get the new version
    new_target_url = r.json()["links"]["latest_draft"]
    
    # upload the not-yet-uploaded files
    for file in to_be_uploaded:
        print("Uploading", file.name)
        # create deposition file (upload a file)
        r_df = requests.post(new_target_url + "/files",
                             data={'name': file.name},
                             files={'file': file.read_bytes()},
                             params={'access_token': args.token})
        
        print("Sent file with status code", r_df.status_code)
    
    # publish the new deposiiton version
    r = requests.post(new_target_url + "/actions/publish",
                      params={'access_token': args.token})

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

        doWrap()

    def on_modified(self, event):
        super(UploadingEventHandler, self).on_modified(event)

        doWrap()




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
        observer.join(1)
except KeyboardInterrupt:
    print("Stopping")
    observer.stop()
observer.join()
