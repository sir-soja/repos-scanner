import os
import sys
import shutil
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
                    print(f"{path}/{file}")
                    leaks.append(f'{file}')
            except UnicodeError or FileNotFoundError:
                pass
    return leaks


def scan_project(project, secret):
    project_name = project.split("/")[-1]
    print(f'> Cloning project {project_name}')
    Repo.clone_from(project, f'{os.getcwd()}/{project_name}')
    print('> Getting remote branches list')
    branch_list = get_remote_branches(project_name)
    print(f'branches : {branch_list}')
    result = dict()
    workdir = os.getcwd()
    for branch in branch_list:
        os.chdir(f'{workdir}/{project_name}')
        result[branch] = parse_for_string(secret)
    return result


def main(secret, path_to_file):
    print('> Getting github projects from text file...')
    project_list = get_all_projects_with_path(path_to_file)
    print(f'projects : {[ p.split("/")[-1] for p in project_list]}')
    output = dict()
    for project in project_list:
        output[project] = scan_project(project, secret)
        print(f'delete project directory')
        delete_project_dir(project)
    print(output)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
