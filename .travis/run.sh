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
    python setup.py install
    conan-package-updater bincrafters ${GITHUB_TOKEN} --ignore --dry-run
else

    python setup.py install
    conan-package-updater bincrafters ${GITHUB_TOKEN} --ignore --dry-run
fi
