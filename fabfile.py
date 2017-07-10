from fabric.api import run, put


def copy_files(local_path, remote_path):
    print(local_path, remote_path)
    run('mkdir -p %s' % remote_path)
    put(local_path, remote_path)
