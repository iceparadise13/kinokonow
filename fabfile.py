import os
from fabric.api import run, put


def copy_files(fab_files, remote_path):
    files_to_deploy = open(fab_files).read().split()
    print('deploying', files_to_deploy)
    run('mkdir -p %s' % remote_path)
    for src in files_to_deploy:
        dest = os.path.join(remote_path, src)
        put(src, dest)
