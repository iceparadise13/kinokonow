FROM python:2-onbuild

ENTRYPOINT ['python', '-m', 'listen.py']
