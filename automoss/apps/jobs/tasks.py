
from django.core.files.uploadedfile import UploadedFile
from ..core.moss import (
    MossResult,
    MossException,
    UnsupportedLanguage,
    MossAPIWrapper
)
import os
import time
from celery.decorators import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task(name='Upload')
def upload_to_moss(user_id, language='c', files=None, base_files=None,
                   is_directory=False, experimental=False,
                   max_matches_until_ignore=1000000, num_to_show=1000000, comment=''):
    """Basic interface for generating a report from MOSS"""

    # TODO validate language and/or auto detect language
    # if language not in self.supported_languages():
    #     raise UnsupportedLanguage(language)

    url = None
    try:
        moss = MossAPIWrapper(user_id)
        moss.connect()  # TODO retries

        if files is None:  # No files supplied
            raise MossException

        if base_files is None:
            base_files = []

        # Set options
        moss.set_directory(is_directory)
        moss.set_experimental(experimental)
        moss.set_max_matches(max_matches_until_ignore)
        moss.set_num_to_show(num_to_show)
        moss.set_language(language)

        data = moss.read()

        # Double check on server-side that language is accepted
        if data == 'no':
            raise UnsupportedLanguage(language)  # Unsupported language
        elif data != 'yes':
            pass

        # TODO determine progress

        # Upload base files
        for base_file in base_files:
            moss.upload_raw_base_file(
                base_file['name'], base_file['file'].encode(), language)

        # Upload submissions
        for index, file_info in enumerate(files, start=1):
            moss.upload_raw_file(
                file_info['name'], file_info['file'].encode(), language, index)

        # Read and return data
        url = moss.generate_url(comment)

        # TODO check for errors
        # b'Error: No files uploaded to compare.\n'

    finally:  # Close session as soon as possible
        moss.close()

    if not url:
        raise MossException('Unable to extract URL')

    result = MossResult(url)

    # TODO do something with result, e.g., write to DB

    return result.url
