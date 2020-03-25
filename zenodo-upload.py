# -*- coding: utf-8 -*-
"""
Uploads to Zenodo via the REST API
"""

import os
import json
import requests
import webbrowser

access_token = ""

# We store our various secrets in an aptly named file
with open('secrets.json') as data_file:
    access_token = json.load(data_file)['access_token']

url = "https://sandbox.zenodo.org/api/deposit/depositions"

description_file = "C:\\Users\\aidan\\Documents\\W8EDU\\psws-zenodo\\test-files\\Readme_5_Mhz Cleveland Heights.txt"
description_text = ""
with open(description_file, 'r') as f:
    description_text = f.read()

# create deposition

data = {
    "metadata": {
        "title": "automatic8 WWV 5MHz Frequency Measurements from Cleveland, OH, USA",
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
                 params={'access_token': access_token})

print(r.status_code)

r.json()

# create deposition file (upload a file)

file_path = 'C:\\Users\\aidan\\Documents\\W8EDU\\psws-zenodo\\test-files\\2020-03-16-WWV5.csv'
file_name = os.path.basename(file_path)

data = {'name': file_name}
files = {'file': open(file_path, 'rb')}
r_df = requests.post(r.json()['links']['files'], data=data, files=files,
                  params={'access_token': access_token})

print(r_df.status_code)

r_df.json()

# publish deposition

r_p = requests.post(r.json()['links']['publish'],
                    params={'access_token': access_token})

print(r_p.status_code)

r_p.json()

webbrowser.open(r_p.json()['links']['record_html'])