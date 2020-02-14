
import argparse
import os
import sys
from time import sleep

from GitRepo import GitRepo
from Sonar import Sonar
from sonarAPI import API
from analysisParser import analysisParseList


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
    api = API()
    git_dir, *_ = os.path.basename(args.repo).rpartition('.git')
    git = GitRepo(os.path.join(args.o, git_dir))
    ok = git.pull_repo_contents(args.repo)
    assert ok
    if os.path.isabs(args.o):
        git_full_path = os.path.join(args.o, git_dir)
    else:
        git_full_path = os.path.join(os.getcwd(), args.o, git_dir)
    print('git_dir:', git_full_path)

    wait('sonarqube', sonar.isSonarQubeRunning, timeout=5)

    before = set(api.projects())
    print(before)
    sonar.runSonarScanner(git_full_path, 'clean', 'verify', 'sonar:sonar')

    wait('analysis', lambda: before.symmetric_difference(api.projects()), timeout=1)

    project_key = before.symmetric_difference(api.projects()).pop()
    print('project_key:', project_key)

    wait('issues', lambda: any(api.issues(project=project_key)), timeout=1)

    issues = list(api.issues(project=project_key))
    issue_file = os.path.join(args.o,  git_dir + '_issues.csv')
    commit_file = os.path.join(args.o,  git_dir + '_commits.csv')
    analysisParseList(issues, issue_file)  # NOTE: NOT TESTED!   Parse and write to file
    # TODO: get commit data for each commit associated with an issue
    #           and write to file
    print(issue_file)
    print(commit_file)
    api.delete_project(project_key)


# parse arguments and start either gui or cli
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--gui', action='store_true', help='start GUI, other options are ignored')
    ap.add_argument('-o', metavar='DIR', default='.', help='output directory, `<DIR>/<REPO>_{issues,commits}.csv`')
    ap.add_argument('repo', metavar='REPO', nargs='?', help='url to git repository to analyse')
    args = ap.parse_args()

    if args.gui:
        ...  # start gui
    elif not args.repo:
        print('Either start with `--gui` or give repository to analyse', file=sys.stderr)
        ap.print_help(sys.stderr)
    else:
        main(args)

