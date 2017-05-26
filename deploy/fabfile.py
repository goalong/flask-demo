#!/usr/bin/env python


import os

from fabric.api import *
from fabric.context_managers import *
from fabric.contrib.project import rsync_project


root_dir = os.path.join(os.getcwd(), '../')

env.hosts = ['107.191.60.109']

env.user = "along"
#env.key = os.path.join(root_dir, Config.get('global', 'key'))
env.password = 'along'

env.local_root = root_dir
env.project_root = "/home/along/flask-demo/"


@parallel
def upload_code():
    rsync_project(
            remote_dir = env.project_root,
            local_dir = env.local_root,
            delete = True,
            exclude=["venv", "deploy", ".git"]
        )

# script_dir = Config.get('server', 'script_dir')
#
# def reload_gunicorn():
# 	with cd(script_dir):
# 		sudo('/bin/bash ./gunicorn reload')

def upload():
    execute(upload_code)

# def reload_test():
#     execute(reload_gunicorn)
