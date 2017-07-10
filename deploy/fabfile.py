import os
from fabric.api import run, put
from fabric.context_managers import cd


def copy_files(fab_files, remote_path):
    files_to_deploy = open(fab_files).read().split()
    print('deploying', files_to_deploy)
    for src in files_to_deploy:
        dest = os.path.join(remote_path, src)
        run('mkdir -p %s' % os.path.dirname(dest))
        put(src, dest)


def deploy(app_name, work_dir, cmd):
    with cd(work_dir):
        run('screen -S %s -X quit' % app_name, warn_only=True)
        # removing the -d flag and purposely attaching for debugging purposes
        # Ctrl+C in the script terminal will detach the session
        run('screen -LS %s -m bash -c "%s"' % (app_name, cmd))
