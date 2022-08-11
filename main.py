"""
Scans each branches of a list of repositories.
Takes the path to the file containing the list and the searched secret as inputs.
This script will clone repositories and checkout every branch to parse each file for secret.
"""

import os
from tqdm import tqdm
import shutil
import argparse
from git import Repo


def get_all_projects_with_path(path_to_file):
    project_list = list()
    file = open(path_to_file, 'r')
    for line in file:
        project_list.append(line.strip('\n'))
    return project_list


def get_remote_branches(project):
    repo = Repo(f'{project}/.git')
    repo.remote().fetch()
    branch_list = [refs.name.replace('origin/', '') for refs in repo.remote().refs]
    branch_list.remove('HEAD')
    return branch_list


def checkout_branch(project, branch):
    repo = Repo(f'{project}/.git')
    repo.remote().fetch()
    repo.git.checkout(branch)
    origin = repo.remotes.origin
    origin.pull()


def delete_project_dir(project):
    try:
        shutil.rmtree(f'{os.getcwd()}/{project.split("/")[-1]}')
    except OSError as error:
        print(f"Error:{error.strerror}")


def parse_for_string(secret):
    leaks = list()
    for path, currentDirectory, files in os.walk(os.getcwd()):
        for file in files:
            try:
                if secret in open(f"{path}/{file}", "r").read():
                    leaks.append(f'{file}')
            except UnicodeError or FileNotFoundError:
                pass
    return leaks


def scan_project(project, secret):
    project_name = project.split("/")[-1]
    Repo.clone_from(project, f'{os.getcwd()}/{project_name}')
    branch_list = get_remote_branches(project_name)
    result = dict()
    for branch in branch_list:
        os.chdir(f'{os.getcwd()}/{project_name}')
        result[branch] = parse_for_string(secret)
        os.chdir('..')
    return result


def main(secret, path_to_file):
    project_list = get_all_projects_with_path(path_to_file)
    output = dict()
    for project in tqdm(project_list, colour='green'):
        output[project] = scan_project(project, secret)
        delete_project_dir(project)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--secret', help='secret you seek in those repositories.')
    parser.add_argument('-f', '--file', help='path to the file containing your list of repositories')
    args = parser.parse_args()
    main(args.secret, args.file)

