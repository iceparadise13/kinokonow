import os
from fabric.api import run, put


def copy_files(fab_files, remote_path):
    files_to_deploy = open(fab_files).read().split()
    print('deploying', files_to_deploy)
    run('mkdir -p %s' % remote_path)
    for f in files_to_deploy:
        put(f, os.path.join(remote_path, f))
