# -*- coding: utf-8 -*-
"""
Uploads to Zenodo via the REST API
"""

import os
import json
import requests
import argparse
import webbrowser

def read_access_token():
    """Reads the access token from `secrets.json` file."""
    try:
        # We store our various secrets in an aptly named file
        with open('secrets.json') as data_file:
            return json.load(data_file)['access_token']
    except FileNotFoundError:
        raise Exception("You must either provide an access token"
                        " on the commnad line or in the file"
                        " `secrets.json`")

parser = argparse.ArgumentParser(
    description="Upload the given file(s) to Zenodo via the REST API."
                " Currently only works with a single file, not directories.")
parser.add_argument('path',
                    default='C:\\Users\\aidan\\Documents\\W8EDU\\psws-zenodo\\test-files\\2020-03-16-WWV5.csv',
                    help="The file(s) to include in the upload.")
# parser.add_argument('-m', '--metadata-file',
#                     help="JSON file containing metadata for the upload.")
parser.add_argument('-t', '--token', default=read_access_token(),
                    help="Access token for the Zenodo account you wish"
                    " to upload to. If no token is specified, the token"
                    " stored in the file `secrets.json` is used.")
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

args = parser.parse_args()

if args.token=="":
    None

if args.sandbox:
    url = "https://sandbox.zenodo.org/api/deposit/depositions"
else:
    url = "https://zenodo.org/api/deposit/depositions"
    

description_file = "C:\\Users\\aidan\\Documents\\W8EDU\\psws-zenodo\\test-files\\Readme_5_Mhz Cleveland Heights.txt"
description_text = ""
with open(description_file, 'r') as f:
    description_text = f.read()

# create deposition

data = {
    "metadata": {
        "title": "automatic12 WWV 5MHz Frequency Measurements from Cleveland, OH, USA",
        "upload_type": "dataset",
        "description": description_text,
        "creators": [
            {"name": "Kazdan, David", "affiliation": "Case Western Reserve University"}
        ],
        "keywords": ["wwv"],
        "communities": [{"identifier": "hamsci-test"}],
        "locations": [
            {
                "lat": 41.493744,
                "lon": -81.578039,
                "place": "location where recordings are made"
            }
        ]
    }
}

headers = {"Content-Type": "application/json"}

r = requests.post(url, data=json.dumps(data), headers=headers,
                 params={'access_token': args.token})

print("Created upload with status code", r.status_code)

# create deposition file (upload a file)

file_name = os.path.basename(args.path)

data = {'name': file_name}
files = {'file': open(args.path, 'rb')}
r_df = requests.post(r.json()['links']['files'], data=data, files=files,
                  params={'access_token': args.token})

print("Sent file with status code", r_df.status_code)

# publish deposition

r_p = requests.post(r.json()['links']['publish'],
                    params={'access_token': args.token})

print("Published upload with status code", r_p.status_code)
print()
print("Response:")
print(json.dumps(r_p.json(), indent=2))

webbrowser.open(r_p.json()['links']['record_html'])
