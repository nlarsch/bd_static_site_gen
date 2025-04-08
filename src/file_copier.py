import logging
import os
import shutil

logger = logging.getLogger(__name__)

def copy_directory(src: str, dest: str) -> None:
    if not (os.path.exists(src) and os.path.isdir(src)):
        raise ValueError("Source directory does not exist")
    if os.path.exists(dest):
        logger.info("Deleting directory " + dest)
        shutil.rmtree(dest)
    os.mkdir(dest)
    for file in os.listdir(src):
        if os.path.isfile(os.path.join(src, file)):
            logger.info("Copying file " + os.path.join(src, file))
            shutil.copy(os.path.join(src, file), dest)
        else:
            logger.info("Copying directory " + os.path.join(src, file))
            copy_directory(os.path.join(src, file), os.path.join(dest, file))

