# Lessons Learned
Aidan Montare

This file attempts to document what I've learned in the process of this project, in the hopes that
it will:
- aid myself in the creation of future projects
- help others in the HamSCI community share their own work
- contribute to the evolving set of best practices in open science projects

This document covers both the upload software and the planned
download/science software, but is hosted just here for now. When I say
'this project', I mean the two packages in a combined sense.

## Guiding Principles
https://www.go-fair.org/fair-principles/

## Fun

Those metadata icon things that you see at the top of everyone's README.md files
can be generated at: https://shields.io/.
GitHub Actions also provides their own versions for some things.

## Resources I used
- https://packaging.python.org/tutorials/packaging-projects/
- https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html

- https://docs.python.org/3/library/pathlib.html
- https://docs.python.org/3/library/argparse.html

## Resources I didn't use (chose the ones above instead)
- https://gist.github.com/stevepeak/5520777

## Reading list
- https://www.citizenscience.gov/
- https://www.citizenscience.org/

- https://spdx.org/using-spdx-license-identifier
Getting the sense that people think its good to have license identifiers in
every file. Perhaps there is an automated way of enforcing this?

Analysis code should perhaps get the licenses of all the data the project uses,
and could give a nice overview report to the user.

- https://github.com/pypa/pipenv/blob/master/README.md
- https://docs.python.org/3.5/howto/logging.html

Zenodo
- Have others done this before?
https://pypi.org/search/?o=&q=zenodo+sync&page=1

CLI's
- https://docs.builtoncement.com/
- https://pypi.org/project/clint/ (has column printing, config file placement)
- Electron? (probably not)

Science-related templates
Python
- Cookiecutter https://github.com/cookiecutter/cookiecutter#data-science
- esp. http://drivendata.github.io/cookiecutter-data-science/
- https://github.com/xuanluong/cookiecutter-python-cli
- https://github.com/audreyr/cookiecutter-pypackage

R
- https://community.rstudio.com/t/data-science-project-template-for-r/3230
