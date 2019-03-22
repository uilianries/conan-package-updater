#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import colorama
import termcolor
import tempfile
import re
import packaging
from github import Github
from github.GithubException import GithubException
from conans.client import conan_api
from conans.errors import ConanException

__author__  = "Uilian Ries"
__license__ = "MIT"
__version__ = '0.1.2'


class PackageUpdater(object):
    """ Execute Conan Packages update
    """

    def __init__(self):
        """ Initialize colorama
        """
        self._arguments = None
        self._organization = None
        self._github = None
        self._conan_instance, _, _ = conan_api.Conan.factory()
        self._updated_repos = {}
        colorama.init()

    def _parse_arguments(self, *args):
        """ Add program arguments

        :param args: User arguments
        """
        parser = argparse.ArgumentParser(description="Conan Package Updater")
        parser.add_argument('organization', type=str, help='Github organization name e.g. bincrafters')
        parser.add_argument('token', type=str, help='Github Token used to create new branches')
        parser.add_argument('--user', '-u', action='store_true', help='Organization is an user account')
        parser.add_argument('--ignore', '-i', action='store_true', help='Ignore errors receive from remote')
        parser.add_argument('--dry-run', '-d', action='store_true', help='Check which packages will be removed only')
        parser.add_argument('--version', '-v', action='version', version='%(prog)s {}'.format(__version__))
        args = parser.parse_args(*args)
        return args

    def _notify_error(self, message):
        """Raise exception or print a message if ignore errors
        """
        if not self._arguments.ignore:
            raise Exception(message)
        print(termcolor.colored(f"ERROR: {message}", 'red'))

    def _notify_info(self, message):
        """Print an information
        """
        print(termcolor.colored(f"INFO: {message}", 'blue'))

    def _notify_warn(self, message):
        """Print an warning
        """
        print(termcolor.colored(f"WARNING: {message}", 'yellow'))

    def run(self, *args):
        """ Process file update

        :param args: User arguments
        """
        self._arguments = self._parse_arguments(*args)
        self._login()
        self._process_conan_repositories()
        self._show_result()

    def _login(self):
        """ Execute Github login
        :return: Github Organization instance
        """
        self._github = Github(login_or_token=self._arguments.token)
        if self._arguments.user:
            self._organization = self._github.get_user(self._arguments.organization)
        else:
            self._organization = self._github.get_organization(self._arguments.organization)
        self._notify_info(f"Logged in the organization '{self._organization.name}'")

    def _process_conan_repositories(self):
        """List all Conan repositories from Github
        :return: List with all Conan projects
        """
        conan_repos = []
        self._notify_info(f"The organization {self._organization.name} contains {self._organization.public_repos} repositories.")
        for repo in self._organization.get_repos():
            try:
                if not repo.name.startswith("conan-"):
                    continue
                if repo.archived:
                    continue

                content = repo.get_contents("conanfile.py")
                self._notify_info(f"Found Conan repository: {repo.name}")

                homepage = self._get_homepage(repo, content)
                if not homepage:
                    continue

                latest_release = self._get_latest_release(repo, homepage)
                if not latest_release:
                    continue

                latest_package = self._get_latest_package(repo)
                if not latest_package:
                    continue

                if packaging.version.parse(latest_release) > packaging.version.parse(latest_package):
                    self._update_repo(repo, latest_package, latest_release)
                else:
                    self._notify_info(f"{repo.name} is up-to-date.")

            except GithubException as error:
                if error.status == 404:
                    pass
                else:
                    self._notify_error(error)
        return conan_repos

    def _get_homepage(self, repository, content):
        self._notify_info(f"Get the homepage from {repository.name}")
        with tempfile.NamedTemporaryFile(prefix="conan", suffix=".py") as file:
            file.write(content.decoded_content)
            file.flush()
            try:
                attributes = self._conan_instance.inspect(file.name, ["homepage"])
                homepage = attributes['homepage']
                if homepage:
                    if "github.com" in homepage:
                        self._notify_info(f"{repository.name} homepage: {homepage}")
                    else:
                        self._notify_warn(f"{repository.name} homepage: {homepage} is not a GitHub repository")
                        homepage = None
                else:
                    self._notify_warn("Could not find 'homepage' in {}".format(repository.name))
                return homepage
            except ConanException as error:
                self._notify_error(error)
            except ImportError as error:
                self._notify_error(error.message)

    def _get_latest_release(self, repository, homepage):
        author_repo = self._github.get_repo(homepage[homepage.find("com/")+4:])
        latest_release = None
        releases = author_repo.get_releases()
        if not releases.totalCount:
            self._notify_warn(f"{repository.name} has not releases. Using tags")
            tags = author_repo.get_tags()
            if tags.totalCount:
                first = tags[0].name[re.search(r'\d', tags[0].name).start():] if re.search(r'\d', tags[0].name) else ""
                last = tags[-1].name[re.search(r'\d', tags[-1].name).start():] if re.search(r'\d', tags[-1].name) else ""
                latest_release = first if first > last else last
        else:
            latest_release = releases[0].tag_name

        if latest_release:
            latest_release = latest_release[re.search(r'\d', latest_release).start():]
            for separator in ['_', '-']:
                if re.search(fr"\d+{separator}\d+{separator}\d+", latest_release):
                    latest_release = latest_release.replace(separator, '.')
                    break

            self._notify_info(f"{repository.name} latest release: {latest_release}")
        else:
            self._notify_warn(f"{repository.name} could not find latest release version")
        return latest_release

    def _get_latest_package(self, repository):
        latest_package = None
        branches = [branch.name[8:] for branch in repository.get_branches() if re.search(r"testing/\d", branch.name)]
        if branches:
            latest_package = branches[0]
            for branch in branches:
                if packaging.version.parse(latest_package) < packaging.version.parse(branch):
                    latest_package = branch
            self._notify_info(f"{repository.name} latest package: {latest_package}")
        else:
            self._notify_warn(f"{repository.name} could not find latest package version")
        return latest_package

    def _update_repo(self, repo, package_release, latest_release):
        commits = repo.get_commits()
        first_commit = next(iter(commits))
        branch = f"testing/{latest_release}"
        self._notify_info(f"{repo.name}: Create branch: {branch}")

        if self._arguments.dry_run:
            self._notify_info(f"{repo.name}: Commit new file (dry-run)")
            self._updated_repos[repo.name] = latest_release
            return

        repo.create_git_ref(f"refs/heads/{branch}", first_commit.sha)
        conanfile = repo.get_contents("conanfile.py", f"testing/{package_release}")
        new_conanfile = repo.get_contents("conanfile.py", f"testing/{latest_release}")
        content = conanfile.decoded_content.replace(package_release.encode(), latest_release.encode())
        self._notify_info(f"{repo.name}: Commit new file")
        repo.update_file(new_conanfile.path, message=f"Bump version to {latest_release}", content=content, sha=new_conanfile.sha, branch=branch)
        self._updated_repos[repo.name] = latest_release

    def _show_result(self):
        if self._updated_repos:
            updated_repos_output = ""
            for repo, version in self._updated_repos.items():
                updated_repos_output += repo + ": " + version + '\n'
            self._notify_info(f"=== UPDATED REPOSITORIES ===\n{updated_repos_output}")
        else:
            self._notify_info(f"=== NO UPDATED REPOSITORIES ===")


def main():
    """ Execute package updater
    """
    try:
        updater = PackageUpdater()
        updater.run(sys.argv[1:])
    except Exception as error:
        print(termcolor.colored("ERROR: {}".format(error), 'red'))
        sys.exit(1)


if __name__ == "__main__":
    main()
