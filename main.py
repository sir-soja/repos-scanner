import os
import sys
import shutil

from git import Repo


def get_all_projects_with_path():
    project_list = list()
    file = open('path_projects.txt', 'r')
    for line in file:
        project_list.append(line.strip('\n'))
    return project_list


def parse_one_project(project_with_path, project, word):
    leaks = dict()
    Repo.clone_from(f'git@github.com:{project_with_path}.git',
                    os.path.join(os.getcwd(), project))
    os.chdir(project)
    list_branches = get_project_branches()
    for branch in list_branches:
        checkout_branch(branch)
        leaks[branch] = parse_for_string(word)
    return leaks


def get_project_branches():
    repo = Repo(f'.git')
    repo.remote().fetch()
    branch_list = [refs.name.replace('origin/', '') for refs in repo.remote().refs]
    return branch_list


def checkout_branch(branch):
    repo = Repo(f'.git')
    repo.remote().fetch()
    repo.git.checkout(branch)
    o = repo.remotes.origin
    o.pull()


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


def delete_repo(workdir, project):
    try:
        shutil.rmtree(f'{workdir}/{project}')
    except OSError as error:
        print(f"Error: {workdir} : {error.strerror}")


def print_res(leaks):
    for project in leaks.keys():
        for branch in leaks[project].keys():
            if leaks[project][branch]:
                for leak in leaks[project][branch]:
                    print(f'> project: {project} - branch: {branch} - file: {leak}')


def main(secret):
    print('start')
    workdir = os.getcwd()
    print('===== GET PROJECTS =====')
    leaks = dict()
    for project_with_path in get_all_projects_with_path():
        project = project_with_path.split('/')[1]
        leaks[project] = parse_one_project(project_with_path, project, secret)
        delete_repo(workdir, project)
        os.chdir(workdir)
    print_res(leaks)
    print('end')


if __name__ == '__main__':
    main(sys.argv[1])
