import logging
import sys

from file_copier import copy_directory
from markdown_processor import generate_pages_recursive

logging.basicConfig(level=logging.INFO)

def main() -> None:
    basepath = sys.argv[1] if sys.argv is not None else "/"
    src = "./static"
    dest = "./public"
    copy_directory(src, dest)
    generate_pages_recursive("./content/", "./template.html", "./docs/", basepath)

if __name__ == "__main__":
    main()