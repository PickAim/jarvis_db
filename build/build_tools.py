from os import system as sys
from build.build_properties import JarvisDatabase


def publish_to_git():
    sys(f'git checkout -b release/{JarvisDatabase}')
    sys('git add .')
    sys(f'git commit -m \"Auto publish {JarvisDatabase}\"')
    sys(f'git push origin release/{JarvisDatabase}')


if __name__ == '__main__':
    publish_to_git()
