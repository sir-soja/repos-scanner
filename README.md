# Repos scanner
This script will clone and checkout every branch of a list of repositories to look for secrets.
It takes two arguments : the secret, the file containing the list of repositories.
It prints a dictionary with the project, the branch and the file where it sees the secret.
## Use it
```bash
pip3 install -r requirements.txt
python3 main.py -s <your_secret> -f <path/to/your/file>
```
Your list of repo has to look like this:
```
https://github.com/repo/1
https://github.com/repo/2
```
This script only works with https git clone for now.# repos-scanner
