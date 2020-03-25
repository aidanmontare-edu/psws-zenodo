# psws-zenodo
Zenodo upload for the HamSCI PSWS project and those running fldigi at home

Currently, you'll need to edit all the variables in the code with the correct paths.
You will also need to create an account at sandbox.zenodo.org and then an access token.
The access token goes in the file secrets.json (an example, sans token, is provided in 
example-secrets.json).

Link for creating access token:

https://sandbox.zenodo.org/account/settings/applications/tokens/new/

Todo:
- command line options
- converting UTF-8 plaintext to html (for the zenodo description)
- handling entire directories and updates
- demon mode
- error handling
- tests
