#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

if [[ "${TRAVIS_EVENT_TYPE}" != "cron" ]]; then
    python setup.py sdist
    pushd tests
    pytest -v -s --cov=conan_package_updater.conan_package_updater
    mv .coverage ..
    popd

    python setup.py install
    conan-package-updater --version
else

    python setup.py install

    conan-package-updater bincrafters ${GITHUB_TOKEN} --ignore
fi
