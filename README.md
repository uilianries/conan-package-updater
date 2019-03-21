[![Build Status: Linux and Macos](https://travis-ci.org/bincrafters/bincrafters-package-updater.svg?branch=master)](https://travis-ci.org/bincrafters/bincrafters-package-updater)
[![Build status: Windows](https://ci.appveyor.com/api/projects/status/github/bincrafters/bincrafters-package-updater?svg=true)](https://ci.appveyor.com/project/bincrafters/bincrafters-package-updater)
[![codecov](https://codecov.io/gh/bincrafters/bincrafters-package-updater/branch/master/graph/badge.svg)](https://codecov.io/gh/bincrafters/bincrafters-package-updater)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/314bf09e0f214735849519143025e6c4)](https://www.codacy.com/app/uilianries/bincrafters-package-updater?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bincrafters/bincrafters-package-updater&amp;utm_campaign=Badge_Grade)
[![Pypi Download](https://img.shields.io/badge/download-pypi-blue.svg)](https://pypi.python.org/pypi/bincrafters-package-updater)

# Conan Package Updater

## A script to update all Conan packages

![logo](logo.png)

#### Requirements
  * Python 3
  * the [Conan](https://conan.io) client

#### INSTALL
To install by pip is just one step

##### Local
If you want to install by local copy

    pip install .

##### Remote
Or if you want to download our pip package

    pip install conan_package_updater
    
##### Github

    pip install git+https://github.com/uilianries/conan-package-updater.git

#### USAGE

```
usage: conan_package_updater.py [-h] [--user] [--yes] [--ignore] [--dry-run]
                                [--version]
                                organization token

Conan Package Updater

positional arguments:
  organization   Github organization name e.g. bincrafters
  token          Github Token used to create new branches

optional arguments:
  -h, --help     show this help message and exit
  --user, -u     Organization is an user account
  --yes, -y      Do not ask for confirmation
  --ignore, -i   Ignore errors receive from remote
  --dry-run, -d  Check which packages will be removed only
  --version, -v  show program's version number and exit
```


###### Update all packages
```

    conan-package-updater bincrafters ${GITHUB_TOKEN}


#### REQUIREMENTS and DEVELOPMENT
To develop or run conan remove outdated

    pip install -r bincrafters_package_updater/requirements.txt


#### UPLOAD
There are two ways to upload this project.

##### Travis CI
After to create a new tag, the package will be uploaded automatically to PyPi.  
Both username and password (encrypted) are in travis file.  
Only one job (Python 3.6) will upload, the others will be skipped.


##### Command line
To upload this package on pypi (legacy mode):

    pip install twine
    python setup.py sdist
    twine upload dist/*


#### LICENSE
[MIT](LICENSE.md)
