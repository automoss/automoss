import argparse
import shutil
from contextlib import closing
import re
import os

import zipfile
import tarfile
import tempfile
import logging

logger = logging.getLogger(__file__)
logging.basicConfig()

VALID_EXTENSIONS = ['py', 'java', 'cc', 'cpp', 'cxx', 'c++', 'h', 'hh', 'hpp',
                    'hxx', 'h++', 'c', 'h', 'cs', 'csx', 'js', 'pl', 'plx', 'pm', 'xs', 't', 'pod', 'asm', 's']


# Handle weird vula renaming
TAR_REGEX = r'tar(\+\d+)*\.?(?P<type>gz|xz|bz2|)$'
ZIP_REGEX = r'\.zip$'


def check_or_extract(file_name, extract_to_path):
    # Returns whether to delete the item afterwards
    if not os.path.exists(file_name):
        return False

    match = None
    if match := re.search(ZIP_REGEX, file_name):
        # https://docs.python.org/3/library/zipfile.html
        with zipfile.ZipFile(file_name, 'r') as zfile:
            zfile.extractall(path=extract_to_path)

    elif match := re.search(TAR_REGEX, file_name):
        # https://docs.python.org/3/library/tarfile.html
        tar_type = match.group('type')
        with closing(tarfile.open(file_name, f'r:{tar_type}')) as tfile:
            for m in tfile.getmembers():
                if '/.' in m.name:  # Hidden
                    continue

                tfile.extract(m.name, path=extract_to_path)

    elif any(file_name.lower().endswith(x) for x in VALID_EXTENSIONS):
        # Valid file, keep it
        return False

    return True  # Delete this file (either invalid extension or is an archive)


def extract_nested(current_file, extract_to, do_remove=False, processed=None):
    if processed is None:
        processed = []

    if current_file in processed:
        return

    processed.append(current_file)

    to_remove = check_or_extract(current_file, extract_to)

    if do_remove and to_remove:
        os.remove(current_file)

    for root, _, files in os.walk(extract_to):

        # Remove hidden files
        files = [f for f in files if f[0] != '.']

        for filename in files:
            next_file = os.path.join(root, filename)
            extract_nested(next_file, root, True, processed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'archive', help="Archive containing student's assignments")
    parser.add_argument('output', help='Output zip archive name (without .zip)')
    args = parser.parse_args()


    logger.setLevel(logging.INFO)

    if not os.path.exists(args.archive):
        print('Could not find input zip')
        return

    current_dir = os.path.abspath('.')

    temp_done_folder = 'temp_done'

    with tempfile.TemporaryDirectory() as tmp_dir:
        extract_nested(args.archive, tmp_dir)

        # Remove mac-specific files
        shutil.rmtree(os.path.join(tmp_dir, '__MACOSX'), ignore_errors=True)

        # Enter temporary directory
        os.chdir(tmp_dir)

        for root, dirs, _ in os.walk('.'):
            for d in dirs:
                if d == 'Submission attachment(s)':
                    parent = os.path.join(root, d)

                    output_filename = os.path.join(temp_done_folder, parent)
                    logger.info(f'Processing {parent}')
                    shutil.make_archive(output_filename, 'zip', parent)

        # Switch back to current directory
        os.chdir(current_dir)

        shutil.make_archive(args.output, 'zip',
                            os.path.join(tmp_dir, temp_done_folder))


if __name__ == '__main__':
    main()
