#!/usr/bin/env python3

import argparse
import os
import sys
from time import sleep
import shutil

from GitRepo import GitRepo
from Sonar import Sonar
from sonarAPI import API
from analysisParser import analysisParseList, analysisParseGit


## Wait for a predicate to be true
# @param message Message to show
# @param predicate Function that returns True, when the wait is over
# @param sleeptime Time in seconds to sleep between calls to predicate
# @param timeout Timeout in minutes (<= 0 is infinite), raises TimeoutException
def wait(message, predicate, *, sleeptime=2, timeout=-1):
    total = 0
    print(f'waiting {message}', end='', file=sys.stderr)
    while not predicate():
        print(end='.', file=sys.stderr)
        sleep(sleeptime)
        total += sleeptime
        if timeout > 0 and total > timeout*60:
            raise TimeoutError(f'timeout expired while waiting: {message}')
    print(file=sys.stderr)


def main(args):
    sonar = Sonar()
    if not sonar.isSonarQubeRunning():
        sonar.startSonarQube()
        print("SonarQube will be started. (This could take a while)")
    api = API()
    git_dir, *_ = os.path.basename(args.repo).rpartition('.git')
    relative_git_path = os.path.join(args.o, git_dir)
    if os.path.exists(relative_git_path):
        print(f'The path `{relative_git_path}` exists, can\'t load the repository', file=sys.stderr)
        print(f'To solve either:', file=sys.stderr)
        print('  a) remove the path', file=sys.stderr)
        print('  b) choose different save directory', file=sys.stderr)
        exit(1)
    try:
        git = GitRepo(relative_git_path)
        ok = git.pullRepoContents(args.repo)
        assert ok
        if os.path.isabs(args.o):
            git_full_path = os.path.join(args.o, git_dir)
        else:
            git_full_path = os.path.join(os.getcwd(), args.o, git_dir)
        print('git_dir:', git_full_path)

        wait('sonarqube', sonar.isSonarQubeRunning, timeout=5)

        before = set(api.projects())
        print(before)
        project_key = None
        scan_started = False
        try:
            sonar.runSonarScanner(git_full_path, 'clean', 'verify', 'sonar:sonar')
            scan_started = True

            # NOTE: this is quite hacky and fragile
            wait('analysis', lambda: before.symmetric_difference(api.projects()), timeout=1)

            project_key = before.symmetric_difference(api.projects()).pop()
            print('project_key:', project_key)

            # NOTE: breaks if there is no issues
            wait('issues', lambda: any(api.issues(project=project_key)), timeout=1)

            issue_file = os.path.join(args.o,  git_dir + '_issues.csv')
            git_file = os.path.join(args.o,  git_dir + '_git.csv')
            git_info = git.getCommitData()

            issues = api.issues(project=project_key)
            analysisParseList(issues, issue_file)  # NOTE: NOT TESTED!   Parse and write to file
            analysisParseGit(git_info, git_file)
        finally:
            if scan_started:
                if project_key is None:
                    wait('analysis', lambda: before.symmetric_difference(api.projects()), timeout=0.2)
                    project_key = before.symmetric_difference(api.projects()).pop()
                # remove analysed project from sonarqube
                api.delete_project(project_key)
    finally:
        # remove git repo
        if os.path.isdir(relative_git_path):
            shutil.rmtree(relative_git_path)


# parse arguments and start either gui or cli
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--gui', action='store_true', help='start GUI, other options are ignored')
    ap.add_argument('-o', metavar='DIR', default='.', help='output directory, `<DIR>/<REPO>_{issues,commits}.csv`')
    ap.add_argument('repo', metavar='REPO', nargs='?', help='url to git repository to analyse')
    args = ap.parse_args()

    if args.gui:
        import run
    elif not args.repo:
        print('Either start with `--gui` or give repository to analyse', file=sys.stderr)
        ap.print_help(sys.stderr)
    else:
        try:
            main(args)
        except KeyboardInterrupt:
            print('interrupted', file=sys.stderr)
            exit(130)

