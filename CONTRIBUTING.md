# Release Process

1. Change the version string in zenodo-upload.py
2. Commit changes.
3. Create a new tag for the release
`git tag -a v0.0.8.post3 -m "0.0.8.post3 testing tags"`
4. Push the changes and the tag to GitHub
5. Will automatically build and transfer to Test PyPI

# Build Process
Taken care of by GitHub

based on https://packaging.python.org/tutorials/packaging-projects

1. `rm -r build/ dist/`
2. `python3 setup.py sdist bdist_wheel`
3. `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`