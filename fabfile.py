import os
from fabric.api import run, put


def copy_files(fab_files, remote_path):
    files_to_deploy = open(fab_files).read().split()
    print('deploying', files_to_deploy)
    for src in files_to_deploy:
        dest = os.path.join(remote_path, src)
        run('mkdir -p %s' % os.path.dirname(dest))
        put(src, dest)


def sync_requirements(requirements_file, remote_path):
    remote_requirements_file = os.path.join(remote_path, requirements_file)
    put(requirements_file, remote_requirements_file)
    run('pip install --no-cache-dir -r ' + remote_requirements_file)
