"""
Load test cases for data center.
"""
import os
import subprocess
from subprocess import DEVNULL
from config import config

data_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

if not os.path.exists(data_root):
    os.makedirs(data_root, mode=0o700, exist_ok=True)

git_url = config.get('Data', 'Git_URL')
# Private key
pkey = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/git-client-key'))

# Specify ssh key for git http://stackoverflow.com/a/29754018/4160550
# And use only public key, not password for ssh
# And avoid SSH's host verification for known hosts
git_env = "GIT_SSH_COMMAND='ssh -i {} -o PreferredAuthentications=publickey -o PasswordAuthentication=no " \
          "-o StrictHostKeyChecking=no'".format(pkey)


def pull_data(data_id):
    try:
        repo_path = os.path.join(data_root, str(data_id))
        repo_url = git_url + 'data/{}'.format(data_id)
        if os.path.exists(repo_path):
            command = "{env} git -C {path} fetch --all && git -C {path} reset --hard origin/master".format(
                env=git_env, path=repo_path)
            return_code = subprocess.call(command, shell=True, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        else:
            command = "{env} git -C {folder} clone {repo_url}".format(env=git_env, repo_url=repo_url, folder=data_root)
            return_code = subprocess.call(command, shell=True, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        if return_code:
            return None
    except Exception as e:
        print(str(e))
        return None
    return repo_path


