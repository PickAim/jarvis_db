import sys
from build_tools import publish_to_git_with_comment

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("[ERROR] invalid argument")
    comment = sys.argv[0]
    publish_to_git_with_comment(comment)
