#!/usr/bin/env python
"""
Gets list of files that will be modified by all PRs for the branch.
Dumps to file to be loaded by other script.
We assume that all PRs we are interested in are made for the master branch.
"""

from github import Github
from github_utils import *
from os.path import expanduser
from repo_config import GH_TOKEN
from argparse import ArgumentParser
import json
import logging

# logger and logger config
# https://docs.python.org/2/library/logger.html
FORMAT = '%(levelname)s - %(funcName)s - %(lineno)d: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser()
    parser.add_argument("-r", "--repo")
    parser.add_argument("-d", "--destination")
    parser.add_argument("-b", "--branch", default='master')
    parser.add_argument("-l", "--logging", default="DEBUG", choices=logging._levelNames, help="Set level of logging")
    args = parser.parse_args()
    logger.setLevel(args.logging)

    gh = Github(login_or_token=open(expanduser(GH_TOKEN)).read().strip())
    repo = gh.get_repo(args.repo)
    pr_list = get_pull_requests(repo, branch=args.branch)

    print("GitHub API rate limit before: {}".format(gh.get_rate_limit()))
    rez = {}
    for pr in pr_list:
        rez[int(pr.number)] = {
            'number': int(pr.number),
            'state': pr.state,
            'created_at': int(pr.created_at.strftime("%s")),
            'updated_at': int(pr.updated_at.strftime("%s")),
            'changed_files_names': pr_get_changed_files(pr)
        }
    with open(args.destination, 'w') as d:
        json.dump(rez, d)

    print("GitHub API rate limit after: {}".format(gh.get_rate_limit()))


if __name__ == '__main__':
    main()
