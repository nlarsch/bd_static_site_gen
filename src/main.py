import logging
import sys

from file_copier import copy_directory
from markdown_processor import generate_pages_recursive

logging.basicConfig(level=logging.INFO)

def main() -> None:
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    src = "./static"
    dest = "./docs"
    copy_directory(src, dest)
    generate_pages_recursive("./content/", "./template.html", dest, basepath)

if __name__ == "__main__":
    main()