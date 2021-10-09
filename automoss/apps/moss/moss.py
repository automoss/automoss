from urllib.parse import urlparse
from bs4 import BeautifulSoup
import socket
import os
import re
import requests
import asyncio
import aiohttp

from ...settings import (
    SUPPORTED_LANGUAGES,
    DEFAULT_MOSS_SETTINGS
)


MOSS_SOCKET_TIMEOUT = 3600 * 2  # 2 hours
MOSS_URL = 'moss.stanford.edu'
HTTP_MOSS_URL = f'http://{MOSS_URL}'
SUPPORTED_MOSS_LANGUAGES = [SUPPORTED_LANGUAGES[language][1]
                            for language in SUPPORTED_LANGUAGES]
HTTP_RETRY_COUNT = 5

ERROR_PREFIX = 'Error: '


def is_valid_moss_url(url):
    """Determine if the url given is a valid url for a MOSS report (correct host)"""
    return url and urlparse(url).netloc == MOSS_URL


class MossException(Exception):
    """Base class for all MOSS Exceptions"""
    pass


class FatalMossException(MossException):
    """A MOSS exception occurred, and we cannot recover. Do not resubmit if this occurs"""
    pass


class UnsupportedLanguage(FatalMossException):
    """Language is not supported by MOSS"""

    def __init__(self, language, **kwargs):
        super().__init__(f'Unsupported language: {language}', **kwargs)


class NoFiles(FatalMossException):
    """MOSS received a request that contained no files"""
    message = 'No files uploaded to compare.'

    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)


class EmptyResponse(FatalMossException):
    """Moss returned nothing after processing a job.

    This means a timeout has occurred and MOSS is potentially
    unable to run this job successfully without altering the options.

    This also occurs if MOSS is under load and is unable to process the
    job, so extra checks are needed to determine whether the job can
    be resubmitted.
    """
    message = 'Empty response.'

    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)


class InvalidRequest(FatalMossException):
    """Moss did not understand this request"""
    pass


class InvalidParameter(FatalMossException):
    """User attempted to set an invalid parameter."""
    pass


class RecoverableMossException(MossException):
    """A MOSS exception occurred, but we are able to recover. Resubmit if this occurs"""
    pass


class ReportError(RecoverableMossException):
    """Base class for report errors"""
    pass


class ReportDownloadTimeout(ReportError):
    """A timeout occurred while downloading the report"""
    pass


class ReportParsingError(ReportError):
    """An error occurred while parsing the report"""
    pass


class InvalidReportURL(ReportError):
    """Attempted to parse an invalid MOSS report URL"""
    pass


class UnparseableMatch(RecoverableMossException):
    """Moss returns a completely incorrectly formatted match document.

    In such a case, the job must be resubmitted.
    """
    pass


class MossConnectionError(RecoverableMossException):
    """A connection error occurred with MOSS. Retry after some time."""
    pass


class MossAPIWrapper:
    """Wrapper class for the MOSS API."""

    _ERRORS = {
        NoFiles.message: NoFiles
    }

    def __init__(self, user_id):
        """Create an API wrapper object.

        :param user_id: The user's MOSS ID
        :type user_id: int
        """
        self.user_id = user_id
        self.socket = socket.socket()

    def connect(self):
        """Connect to the MOSS server"""
        self.socket.connect((MOSS_URL, 7690))
        self.socket.settimeout(MOSS_SOCKET_TIMEOUT)
        self._send_string(f'moss {self.user_id}')  # authenticate user

    def close(self):
        """Close the MOSS connection"""
        try:
            self._send_string('end')
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            return True
        except ConnectionError:
            return False  # Do not throw error if unable to close

    def read_raw(self, buffer):
        """Read the raw information in the socket's buffer"""
        return self.socket.recv(buffer)

    def read(self, buffer=1024):
        """Read the information in the socket's buffer as a string"""
        return self.read_raw(buffer).decode().rstrip('\n')

    def set_directory(self, is_directory=True):
        """Set the upload to be directory mode

        :param is_directory: Whether the upload is in directory mode, defaults to True
        :type is_directory: bool, optional
        """
        self._send_string(f'directory {is_directory:d}')

    def set_experimental(self, experimental=True):
        """Set the upload to use the experimental server

        :param experimental: Whether the upload should be experimental, defaults to True
        :type experimental: bool, optional
        """
        self._send_string(f'X {experimental:d}')

    def set_max_matches(self, max_matches):
        """Set the max number of matches until ignored

        :param max_matches: Max number of matches until ignored
        :type max_matches: int
        :raises InvalidParameter: If max_matches < 1
        """
        if max_matches < 1:
            raise InvalidParameter(
                f'Max matches must be positive ({max_matches} is invalid).')
        self._send_string(f'maxmatches {max_matches}')

    def set_max_displayed_matches(self, max_displayed_matches):
        """Set the max number of displayed matches

        :param max_displayed_matches: max number of displayed matches
        :type max_displayed_matches: int
        :raises InvalidParameter: If max_displayed_matches < 1
        """
        if max_displayed_matches < 1:
            raise InvalidParameter(
                f'Max displayed matches must be positive ({max_displayed_matches} is invalid).')
        self._send_string(f'show {max_displayed_matches}')

    def set_language(self, language):
        """Set the language of the job

        :param language: Language of the job.
        :type language: str
        :raises UnsupportedLanguage: If language is unsupported (not in SUPPORTED_MOSS_LANGUAGES)
        """
        if language not in SUPPORTED_MOSS_LANGUAGES:
            raise UnsupportedLanguage(language)

        self._send_string(f'language {language}')

    def upload_raw_file(self, file_path, bytes, language, file_id, use_basename=False):
        """Upload raw file to MOSS"""

        size = len(bytes)

        if use_basename:
            file_path = os.path.basename(file_path)

        # Replace whitespace with _
        file_name = re.sub(r'\s+', '_', file_path).replace('\\', '/')

        # Send file header information
        self._send_string(f'file {file_id} {language} {size} {file_name}')

        # Send actual file info
        self._send_raw(bytes)

    def upload_raw_base_file(self, file_path, bytes, language, use_basename=False):
        """Upload raw base file to MOSS"""

        self.upload_raw_file(file_path, bytes, language, 0, use_basename)

    def upload_base_file(self, file_path, language, use_basename=False):
        """Upload base file to MOSS"""

        self.upload_file(file_path, language, 0, use_basename)

    def upload_file(self, file_path, language, file_id, use_basename=False):
        """Upload file to MOSS"""

        with open(file_path, 'rb') as f:
            self.upload_raw_file(file_path, f.read(),
                                 language, file_id, use_basename)

    def process(self, comment=''):
        """Process the Job and return the generated report URL.

        :param comment: Name of the job, defaults to ''
        :type comment: str, optional
        :return: Generated report URL
        :rtype: str
        """
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
        """Create a MossMatch object, given the HTML"""

        try:
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table')
            rows = iter(table.find_all('tr'))

            header = next(rows)

            a, _, b, _, _ = header.find_all('th')
            self.name_1, self.percentage_1 = self._parse_name_percentage(a)
            self.name_2, self.percentage_2 = self._parse_name_percentage(b)

            # Possible to reconstruct (more accurate) percentages from line matches
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
        """Create a Result object from a MOSS URL

        :param url: The MOSS URL
        :type url: str
        """
        self.url = url
        self.matches = list(self._parse_matches(url))

    # https://stackoverflow.com/a/54878794
    async def _fetch(self, session, url):
        error = None
        for _ in range(HTTP_RETRY_COUNT):
            try:
                async with session.get(url, raise_for_status=True) as resp:
                    return await resp.text()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                error = e  # Retry

        raise ReportDownloadTimeout(error)

    async def _fetch_concurrent(self, urls):
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            tasks = [loop.create_task(self._fetch(session, u))
                     for u in urls]
            return [await result for result in asyncio.as_completed(tasks)]

    def _parse_matches(self, url):
        base_url = f"{url.rstrip('/')}/"  # Ensure link ends with a /
        req = requests.get(base_url, verify=False)
        if req.status_code != 200:
            raise ReportParsingError(
                f'Invalid status code ({req.status_code})')

        # Possible to parse errors here
        html = req.text

        num_matches = html.count('<TR>') - 1

        urls = [f'{base_url}match{i}-top.html' for i in range(num_matches)]
        responses = asyncio.run(self._fetch_concurrent(urls))

        for response in responses:
            try:
                yield MossMatch(response)
            except UnparseableMatch:
                pass


class MOSS:

    @classmethod
    def validate_moss_id(cls, user_id, raise_if_connection_error=False):
        """Validate the MOSS ID of a user"""

        moss = MossAPIWrapper(user_id)
        try:
            moss.connect()
            moss.process()
        except NoFiles:
            return True
        except Exception as e:  # Anything else means no
            if raise_if_connection_error and isinstance(e, ConnectionError):
                raise e
            return False
        finally:  # Close session as soon as possible
            moss.close()

    @classmethod
    def generate(cls, **kwargs):
        """All-in-one method for generating a MOSS report"""

        url = cls.generate_url(**kwargs)
        return cls.generate_report(url)

    @classmethod
    def generate_report(cls, url):
        """Generate a MOSS report, given a valid URL"""

        if not is_valid_moss_url(url):
            raise InvalidReportURL(f'Invalid report url: "{url}"')

        try:
            return Result(url)

        except ReportParsingError:
            raise

        except Exception as e:
            raise ReportParsingError(f'Malformed Report: {url}. Error: {e}')

    @classmethod
    def callback(cls, f, *args, **kwargs):
        """Run callback function"""

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
            moss.connect()

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
                raise UnsupportedLanguage(language)  # Unsupported language
            elif data == '':
                raise EmptyResponse
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
            raise MossConnectionError(e.strerror)

        finally:  # Close session as soon as possible
            moss.close()

        return url
