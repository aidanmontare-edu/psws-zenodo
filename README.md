# psws-zenodo

![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/v/tag/aidanmontare-edu/psws-zenodo?include_prereleases&sort=semver)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/aidanmontare-edu/psws-zenodo?include_prereleases)
![Upload Python Package](https://github.com/aidanmontare-edu/psws-zenodo/workflows/Upload%20Python%20Package/badge.svg)
![PyPI](https://img.shields.io/pypi/v/psws-zenodo)  
![Linting](https://github.com/aidanmontare-edu/psws-zenodo/workflows/Linting/badge.svg)

Zenodo upload for the HamSCI PSWS project and those running fldigi at home

*This is only a proof of concept. It is still in a very rough phase, and has
very little error checking.*


## Installation

**Note: While this code is published as a test package, the packaged form does
not work correctly yet. For now, you should download or clone the git repository
directly, rather than trying to use PyPI**

### To download from source:

`git clone https://github.com/aidanmontare-edu/psws-zenodo.git`

or download a .zip from the github page.

### To install from PyPI:

This project is currently
[hosted on the Test PyPI server](https://test.pypi.org/project/psws-zendo/).
You can download it from there by running (assuming your system has pip for
Python 3 as `pip3`):

`pip3 install --upgrade -i https://test.pypi.org/simple/ --no-deps psws-zendo`

Once you have this, you should follow the setup instructions below.

In the future, this project will be hosted on the main Python Package Index.


## Setup and Usage

To use:

1. Create an account at sandbox.zenodo.org and then an access token. Your
access token must have both the `deposit:action` and the `deposit:write` scopes.
2. Rename/copy the `example-config` directory as `config`, and set your
configuration settings in each file. There are several to set:

The access token goes in the file `secrets.json`
(an example, sans token, has been provided).

In the file
`current-target.json`, "onZenodoSandboxServer" is either
1 if you are using sandbox.zenodo.org, or 0 for zenodo.org. We'll get the
value of "id" once we create a Zenodo upload.

Also in that file, the path to the files you wish to have uploaded to Zenodo
(i.e. your data) should be set as `local_path`. You can also specify this as a
command line argument.

3. From the Zenodo website, create a new Zenodo upload and specify all the
metadata you want to appear once your data is published. For instance, you
might want to add your data to the HamSCI community so that it can be found
by others!
4. Save your changes. Once you hit save, the ID for the object you've just
created should show up in the URL bar in your browser. The ID is the number at
the end of the URL (for instance, the "518035" in
https://sandbox.zenodo.org/deposit/518035) Copy this ID.
5. Paste the ID into `current-target.json`.
6. That should be all the configuration. Try running the script, and see what
happens.

You should be able to run the script with `python3 psws-zenodo.py` or
`psws-zenodo.py`. Note that reading the config files may not work yet if you
are not in the same directory as `psws-zenodo.py`.



Links for creating an access token:

Sandbox: https://sandbox.zenodo.org/account/settings/applications/tokens/new/  
Regular: https://zenodo.org/account/settings/applications/tokens/new/


## Crontab entry

A crontab entry like the following will run the script every day and upload to
the Zenodo sandbox while sending program output (for debugging) to a text file.

```
00 01 * * * cd /home/pi/psws-zenodo/ ; python3 /home/pi/psws-zenodo/zenodo-upload.py -s >> /home/pi/psws-zenodo/logs.txt
```

Note that this will create a new DOI for every day's data. This might be
wasteful to run on a server that is not the sandbox. Future updates to this
program might operate differently to try to address this.


## Todo

- converting UTF-8 plaintext to html (for the zenodo description)
- handling entire directories and updates
- demon mode
- error handling
- restructure request-making to raise exceptions with bad http responses
- tests
- support for both sandbox and regular servers
- licensing
- notice to user about picking license
- https://requests-oauthlib.readthedocs.io/en/latest/examples/github.html
- https://docs.python.org/3.5/library/enum.html
- I think eventually the entry_points option will be better.

```
entry_points={
        "console_scripts": [
            "pip=pip._internal.cli.main:main",
```

https://packaging.python.org/guides/distributing-packages-using-setuptools/#entry-points
