from datetime import datetime
from os import system as sys
from build_properties import JarvisDatabase


def publish_to_git():
    sys(f'git checkout -b release/{JarvisDatabase}')
    sys('git add ..')
    sys(f'git commit -m \"[Auto: {datetime.now()}] publish {JarvisDatabase}\"')
    sys(f'git push origin release/{JarvisDatabase}')


def publish_to_git_with_comment(comment):
    sys(f'git checkout -b release/{JarvisDatabase}')
    sys('git add ..')
    sys(f'git commit -m \"{comment}\"')
    sys(f'git push origin release/{JarvisDatabase}')
