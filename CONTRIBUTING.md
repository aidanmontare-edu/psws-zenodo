# Build Process
very manual

based on https://packaging.python.org/tutorials/packaging-projects

1. `rm -r build/ dist/`
2. `python3 setup.py sdist bdist_wheel`
3. `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
