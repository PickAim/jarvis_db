import os
from datetime import datetime
from os import system as sys
from build_constants import _separator, element_name


def get_my_version() -> str:
    with(open(__file__.replace(os.path.basename(__file__), '') + 'build.properties', 'r') as properties):
        line = properties.readline()
        version = ''
        while line != "":
            name = line.split(_separator)[0]
            if name == element_name:
                version = line.split(_separator)[1]
                break
            line = properties.readline()
        if version == '':
            print('[ERROR] Invalid build.properties file format')
        version = version.replace('\n', '')
        return version


def publish_to_git():
    version = get_my_version()
    sys(f'git checkout -b release/{version}')
    sys('git add ..')
    sys('git add .')
    sys(f'git commit -m \"[Auto: {datetime.now()}] publish {version}\"')
    sys(f'git push origin release/{version}')


def publish_to_git_with_comment(comment):
    version = get_my_version()
    sys(f'git checkout -b release/{version}')
    sys('git add ..')
    sys('git add .')
    sys(f'git commit -m \"{comment}\"')
    sys(f'git push origin release/{version}')
