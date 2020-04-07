# psws-zenodo
Zenodo upload for the HamSCI PSWS project and those running fldigi at home

*This is only a proof of concept. It is still in a very rough phase, and has
very little error checking.*

To install:

This project is currently
(hosted on the Test PyPI server)[https://test.pypi.org/project/psws-zendo/].
You can download it from there by running (assuming your system has pip for 
Python 3 as `pip3`):

`pip3 install --upgrade -i https://test.pypi.org/simple/ --no-deps psws-zendo`

In the future, this project will be hosted on the main Python Package Index.

To use:

1. Edit the script place your default path in for `--path`, or get used to
supplying the command line argument.
2. Create an account at sandbox.zenodo.org and then an access token.
3. Rename/copyy the `example-config` directory as `config`, and set your
configuration settings. The access token goes in the file `secrets.json`
(an example, sans token, has been provided). In the file
`current-target.json`, "onZenodoSandboxServer" is either
1 if you are using sandbox.zenodo.org, or 0 for zenodo.org. We'll get the
value of "id" once we create a Zenodo upload.
4. From the Zenodo website, create a new Zenodo upload and specify all the
metadata you want to appear once your data is published. For instance, you
might want to add your data to the HamSCI community so that it can be found
by others!
6. Save your changes. Once you hit save, the ID for the object you've just
created should show up in the URL bar in your browser. The ID is the number at
the end of the URL (for instance, the "518035" in
https://sandbox.zenodo.org/deposit/518035) Copy this ID.
7. Paste the ID into `current-target.json`.
8. That should be all the configuration. Try running the script, and see what
happens.


Link for creating access token:

https://sandbox.zenodo.org/account/settings/applications/tokens/new/

Todo:
- actually using the command line options
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

