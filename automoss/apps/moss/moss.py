from bs4 import BeautifulSoup
import socket
import os
import re
import requests
import time

import threading

import asyncio
import aiohttp

from ...settings import (
    SUPPORTED_LANGUAGES,
    DEFAULT_MOSS_SETTINGS
)

from django.utils.http import url_has_allowed_host_and_scheme

MOSS_URL = 'moss.stanford.edu'
SUPPORTED_MOSS_LANGUAGES = [SUPPORTED_LANGUAGES[l][1]
                            for l in SUPPORTED_LANGUAGES]


def is_valid_moss_url(url):
    return url and url_has_allowed_host_and_scheme(url, MOSS_URL)


class MossException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FatalMossException(MossException):
    """ Cannot recover. Do not resubmit if this occurs """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnsupportedLanguage(FatalMossException):
    def __init__(self, language, **kwargs):
        super().__init__(f'Unsupported language: {language}', **kwargs)


class NoFiles(FatalMossException):
    message = 'No files uploaded to compare.'

    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)


class EmptyResponse(FatalMossException):
    """Moss returned nothing after requesting for URL.

    This means a timeout has occurred and MOSS is unable to run this
    job successfully without altering the options.
    """
    message = 'Empty response.'

    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)


class InvalidRequest(FatalMossException):
    """Moss did not understand this request"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InvalidParameter(FatalMossException):
    """User attempted to set an invalid parameter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RecoverableMossException(MossException):
    """ Able to recover. Resubmit if this occurs """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReportDownloadTimeout(RecoverableMossException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnparseableMatch(RecoverableMossException):
    # Moss returns a completely incorrecly formatted match document
    # e.g. http://moss.stanford.edu/results/0/3222848531763
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MossConnectionError(RecoverableMossException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ERROR_PREFIX = 'Error: '


class MossAPIWrapper:

    _ERRORS = {
        NoFiles.message: NoFiles
    }

    def __init__(self, user_id):
        self.user_id = user_id
        self.socket = socket.socket()

    def connect(self):
        # TODO add retries
        self.socket.connect((MOSS_URL, 7690))
        self._send_string(f'moss {self.user_id}')  # authenticate user

    def close(self):
        try:
            self._send_string('end')
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            return True
        except ConnectionError as e:
            return False  # Do not throw error if unable to close

    def read_raw(self, buffer):
        return self.socket.recv(buffer)

    def read(self, buffer=1024):
        return self.read_raw(buffer).decode().rstrip('\n')

    def set_directory(self, is_directory=True):
        self._send_string(f'directory {is_directory:d}')

    def set_experimental(self, experimental=True):
        self._send_string(f'X {experimental:d}')

    def set_max_matches(self, max_matches):
        if max_matches < 1:
            raise InvalidParameter(
                f'Max matches must be positive ({max_matches} is invalid).')
        self._send_string(f'maxmatches {max_matches}')

    def set_max_displayed_matches(self, max_displayed_matches):
        if max_displayed_matches < 1:
            raise InvalidParameter(
                f'Max displayed matches must be positive ({max_displayed_matches} is invalid).')
        self._send_string(f'show {max_displayed_matches}')

    def set_language(self, language):
        if language not in SUPPORTED_MOSS_LANGUAGES:
            raise UnsupportedLanguage(language)

        self._send_string(f'language {language}')

    def upload_raw_file(self, file_path, bytes, language, file_id, use_basename=False):

        size = len(bytes)

        if use_basename:
            file_path = os.path.basename(file_path)

        # Replace whitespace with _
        file_name = re.sub('\s+', '_', file_path).replace('\\', '/')

        # Send file header information
        self._send_string(f'file {file_id} {language} {size} {file_name}')

        # Send actual file info
        self._send_raw(bytes)

    def upload_raw_base_file(self, file_path, bytes, language, use_basename=False):
        self.upload_raw_base(file_path, bytes, language, 0, use_basename)

    def upload_base_file(self, file_path, language, use_basename=False):
        self.upload_file(file_path, language, 0, use_basename)

    def upload_file(self, file_path, language, file_id, use_basename=False):
        with open(file_path, 'rb') as f:
            self.upload_raw_file(file_path, f.read(),
                                 language, file_id, use_basename)

    def process(self, comment=''):
        # Send final query
        self._send_string(f'query 0 {comment}')

        data = self.read()
        if is_valid_moss_url(data):
            return data

        # Not a valid URL, check for errors
        if data.startswith(ERROR_PREFIX):
            error_message = data[len(ERROR_PREFIX):]

            error = self._ERRORS.get(error_message)
            if error:  # Found corresponding error
                raise error

            # TODO find errors like this
            raise FatalMossException(f'Unknown error: {error_message}')

        elif data:
            raise FatalMossException(f'Data extracted: "{data}"')

        raise EmptyResponse

    def _send_raw(self, bytes):
        self.socket.send(bytes)

    def _send_string(self, text):
        return self._send_raw(f'{text}\n'.encode())


class MossMatch:
    def __init__(self, html):
        try:
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table')
            rows = iter(table.find_all('tr'))

            header = next(rows)

            a, _, b, _, _ = header.find_all('th')
            self.name_1, self.percentage_1 = self._parse_name_percentage(a)
            self.name_2, self.percentage_2 = self._parse_name_percentage(b)

            # TODO reconstruct (more accurate) percentages from line matches?
            self.line_matches = []
            self.lines_matched = 0
            for tr in rows:
                a, _, b, _ = tr.find_all('td')
                first, second = [self._parse_from_to(x) for x in (a, b)]
                self.line_matches.append({
                    'first': first,
                    'second': second
                })

                self.lines_matched += max(x['to'] - x['from']
                                          for x in (first, second)) + 1
        except Exception:
            raise UnparseableMatch

    def _parse_from_to(self, tag):
        info = list(map(int, tag.get_text(strip=True).split('-')))
        return {
            'from': info[0],
            'to': info[1]
        }

    def _parse_name_percentage(self, tag):
        return re.search(r'(\S+)\s+\((\d+)%\)', tag.get_text(strip=True)).groups()

    def __str__(self):
        return f'{self.name_1} ({self.percentage_1}%) : {self.name_2} ({self.percentage_2}%) | {self.line_matches}'


class Result:

    def __init__(self, url):
        # Parse a moss result from a URL
        self.url = url
        self.matches = list(self._parse_matches(url))

    # https://stackoverflow.com/a/54878794
    async def fetch(self, session, url):
        async with session.get(url) as resp:
            return await resp.text()

    async def fetch_concurrent(self, urls):
        try:
            loop = asyncio.get_event_loop()
            async with aiohttp.ClientSession() as session:
                tasks = [loop.create_task(self.fetch(session, u))
                         for u in urls]
                return [await result for result in asyncio.as_completed(tasks)]
        except asyncio.TimeoutError as e:
            raise ReportDownloadTimeout(e)

    def _parse_matches(self, url):
        base_url = f"{url.rstrip('/')}/"  # Ensure link ends with a /
        html = requests.get(base_url, verify=False).text

        # TODO parse errors?
        num_matches = html.count('<TR>') - 1

        urls = [f'{base_url}match{i}-top.html' for i in range(num_matches)]
        responses = asyncio.run(self.fetch_concurrent(urls))

        for response in responses:
            try:
                yield MossMatch(response)
            except UnparseableMatch:
                pass

class MOSS:

    @classmethod
    def validate_moss_id(cls, user_id):
        moss = MossAPIWrapper(user_id)
        try:
            moss.connect()
            moss.process()
        except NoFiles:
            return True
        except Exception:  # Anything else means no
            return False
        finally:  # Close session as soon as possible
            moss.close()

    @classmethod
    def generate(cls, **kwargs):
        url = cls.generate_url(**kwargs)
        return cls.generate_report(url)

    @classmethod
    def generate_report(cls, url):
        try:
            return Result(url)

        except Exception as e:
            if is_valid_moss_url(url):
                # Some timeout error?
                # TODO add built-in retry functionality to parsing report
                raise RecoverableMossException(
                    f'Unable to generate report: {e}')
            else:
                raise FatalMossException(f'Unable to generate report: {e}')

    @classmethod
    def callback(cls, f, *args, **kwargs):
        if f and callable(f):
            f(*args, **kwargs)

    @classmethod
    def generate_url(cls, user_id, language=SUPPORTED_MOSS_LANGUAGES[0],
                     files=None, base_files=None, is_directory=False,
                     experimental=False,
                     max_until_ignored=DEFAULT_MOSS_SETTINGS['max_until_ignored'],
                     max_displayed_matches=DEFAULT_MOSS_SETTINGS['max_displayed_matches'],
                     comment='', use_basename=False,

                     # Define callbacks
                     on_start=None,
                     on_connect=None,
                     on_file_upload=None,  # Called for every file
                     on_base_file_upload=None,  # Called for every base file

                     on_upload_start=None,
                     on_upload_finish=None,

                     on_processing_start=None,
                     on_processing_finish=None
                     ):
        """Basic interface for generating a report from MOSS"""

        # TODO auto detect language
        cls.callback(on_start)

        # Returns report
        if language not in SUPPORTED_MOSS_LANGUAGES:
            raise UnsupportedLanguage(language)

        url = None
        try:
            if files is None:
                raise MossException('No files supplied')

            if base_files is None:
                base_files = []

            moss = MossAPIWrapper(user_id)
            moss.connect()  # TODO retries

            cls.callback(on_connect)

            # Set options
            moss.set_directory(is_directory)
            moss.set_experimental(experimental)
            moss.set_max_matches(max_until_ignored)
            moss.set_max_displayed_matches(max_displayed_matches)
            moss.set_language(language)

            data = moss.read()
            # Double check on server-side that language is accepted
            if data == 'no':
                # TODO detect incorrect options?
                raise UnsupportedLanguage(language)  # Unsupported language
            elif data != 'yes':
                raise InvalidRequest(
                    f'Moss did not understand this request. Response: "{data}"')

            cls.callback(on_upload_start)

            # Upload base files
            for base_file in base_files:
                moss.upload_base_file(base_file, language, use_basename)
                cls.callback(on_base_file_upload, base_file)

            # Upload submissions
            for index, path in enumerate(files, start=1):
                moss.upload_file(path, language, index, use_basename)
                cls.callback(on_file_upload, path)

            cls.callback(on_upload_finish)

            # Read and return data
            cls.callback(on_processing_start)
            url = moss.process(comment)
            cls.callback(on_processing_finish)

        except ConnectionError as e:
            # Includes:
            #  - BrokenPipeError
            #  - ConnectionAbortedError
            #  - ConnectionRefusedError
            #  - ConnectionResetError.
            raise MossConnectionError(e)

        finally:  # Close session as soon as possible
            moss.close()

        return url
