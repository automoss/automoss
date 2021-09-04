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

from django.utils.http import url_has_allowed_host_and_scheme

MOSS_URL = 'moss.stanford.edu'
SUPPORTED_MOSS_LANGUAGES = [SUPPORTED_LANGUAGES[l][1]
                            for l in SUPPORTED_LANGUAGES]


def is_valid_moss_url(url):
    return url_has_allowed_host_and_scheme(url, MOSS_URL)


class MossAPIWrapper:

    def __init__(self, user_id):
        self.user_id = user_id
        self.socket = socket.socket()

    def connect(self):
        # TODO add retries
        try:
            self.socket.connect((MOSS_URL, 7690))
            self._send_string(f'moss {self.user_id}')  # authenticate user
        except ConnectionRefusedError as e:
            raise MossException(f'Connection Refused: "{e}"')

    def close(self):
        try:
            self._send_string('end')
            self.socket.close()
        except Exception as e:
            raise MossException(f'Unable to close moss session: "{e}"')

    def read_raw(self, buffer):
        return self.socket.recv(buffer)

    def read(self, buffer=1024):
        return self.read_raw(buffer).decode().rstrip('\n')

    def set_directory(self, is_directory=True):
        self._send_string(f'directory {is_directory:d}')

    def set_experimental(self, experimental=True):
        self._send_string(f'X {experimental:d}')

    def set_max_matches(self, max_matches):
        self._send_string(f'maxmatches {max_matches}')

    def set_max_displayed_matches(self, max_displayed_matches):
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
        return self.read()

    def _send_raw(self, bytes):
        self.socket.send(bytes)

    def _send_string(self, text):
        return self._send_raw(f'{text}\n'.encode())


class MossMatch:
    def __init__(self, html):
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
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            tasks = [loop.create_task(self.fetch(session, u)) for u in urls]
            return [await result for result in asyncio.as_completed(tasks)]

    def _parse_matches(self, url):
        html = requests.get(url, verify=False).text

        # TODO parse errors?
        num_matches = html.count('<TR>') - 1

        urls = [f'{url}/match{i}-top.html' for i in range(num_matches)]
        responses = asyncio.run(self.fetch_concurrent(urls))

        for response in responses:
            yield MossMatch(response)


class MossException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnsupportedLanguage(MossException):
    def __init__(self, language, **kwargs):
        super().__init__(f'Unsupported language: {language}', **kwargs)


class MOSS:
    def __init__(self, user_id):
        self.user_id = user_id

    def generate(self, **kwargs):
        url = self.generate_url(**kwargs)
        return self.generate_report(url)

    def generate_report(self, url):
        try:
            return Result(url)
        except Exception as e:
            raise MossException(f'Unable to generate report: {e}')

    def generate_url(self, language=SUPPORTED_MOSS_LANGUAGES[0],
                     files=None, base_files=None, is_directory=False,
                     experimental=False,
                     max_until_ignored=DEFAULT_MOSS_SETTINGS['max_until_ignored'],
                     max_displayed_matches=DEFAULT_MOSS_SETTINGS['max_displayed_matches'],
                     comment='', use_basename=False):
        """Basic interface for generating a report from MOSS"""

        # TODO auto detect language

        # Returns report
        if language not in SUPPORTED_MOSS_LANGUAGES:
            raise UnsupportedLanguage(language)

        url = None
        try:
            if files is None:
                raise MossException('No files supplied')

            if base_files is None:
                base_files = []

            moss = MossAPIWrapper(self.user_id)
            moss.connect()  # TODO retries

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
            elif data != 'yes':
                pass

            # Upload base files
            for base_file in base_files:
                moss.upload_base_file(base_file, language, use_basename)

            # Upload submissions
            for index, path in enumerate(files, start=1):
                moss.upload_file(path, language, index, use_basename)

            # Read and return data
            data = moss.process(comment)

            if is_valid_moss_url(data):
                url = data
            else:
                raise MossException(f'Data extracted: "{data}"')

        except Exception as e:
            raise MossException(f'Exception: "{e}"')

        finally:  # Close session as soon as possible
            moss.close()

        if not url:
            raise MossException('Unable to extract URL')

        return url
