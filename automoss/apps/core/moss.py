import socket
import os
import re
import requests

import numpy as np
import asyncio
import aiohttp


from ...defaults import (
    DEFAULT_MOSS_LANGUAGE,
    MAX_UNTIL_IGNORED,
    MAX_DISPLAYED_MATCHES,
    SUPPORTED_MOSS_LANGUAGES
)

class MossAPIWrapper:

    def __init__(self, user_id):
        self.user_id = user_id
        self.socket = socket.socket()

    def connect(self):
        # TODO add retries
        self.socket.connect(('moss.stanford.edu', 7690))
        self._send_string(f'moss {self.user_id}')  # authenticate user

    def close(self):
        self._send_string('end')
        self.socket.close()

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

    def set_num_to_show(self, num_to_show):
        self._send_string(f'show {num_to_show}')

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
            self.upload_raw_file(file_path, f.read(), language, file_id, use_basename)

    def generate_url(self, comment=''):
        # Send final query
        self._send_string(f'query 0 {comment}')
        return self.read()

    def _send_raw(self, bytes):
        self.socket.send(bytes)

    def _send_string(self, text):
        return self._send_raw(f'{text}\n'.encode())


class MatchItem:
    # Meaningless alone, must be paired with another match item in Match class
    def __init__(self, id, percentage, html):
        self.id = id
        self.percentage = float(percentage)
        self.html = html

        self._parse_from_html(html)

    def _parse_from_html(self, html):
        pass  # TODO

    def __str__(self):
        return f'({self.id}, {self.percentage}%)'


class Match:
    def __init__(self, first, second, lines_matched):
        self.first = first
        self.second = second
        self.lines_matched = int(lines_matched)

    def __str__(self):
        return f'{self.first} : {self.second}% | {self.lines_matched}'


class MossResult:

    def __init__(self, url):
        # Parse a moss result from a URL
        self.url = url
        self.matches = []

        self._parse_from_url(url)

    # https://stackoverflow.com/a/54878794
    async def fetch(self, session, url):
        async with session.get(url) as resp:
            return await resp.text()

    async def fetch_concurrent(self, urls):
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            tasks = [loop.create_task(self.fetch(session, u)) for u in urls]
            return [await result for result in asyncio.as_completed(tasks)]

    def _generate_urls(self, base_url, num_matches):
        for i in range(num_matches):
            # yield f'{base_url}/match{i}.html'
            for j in (0, 1):
                yield f'{base_url}/match{i}-{j}.html'

    _MATCH_LINK = r'<A[^>]+>(\S+)\s+\((\d+)%\)</A>[^<]+<TD'
    _PARSE_MATCH = f'{_MATCH_LINK}>{_MATCH_LINK}[^>]+>(\d+)'

    def _parse_from_url(self, url):

        initial_info = requests.get(url, verify=False)
        html = initial_info.text

        matches = re.findall(self._PARSE_MATCH, html)
        urls = self._generate_urls(url, len(matches))

        data = asyncio.run(self.fetch_concurrent(urls))
        responses = np.reshape(data, (-1, 2))

        for match, response in zip(matches, responses):
            left = MatchItem(*match[0:2], response[0])
            right = MatchItem(*match[2:4], response[1])
            self.matches.append(Match(left, right, match[4]))

    def json(self):
        return {'url': self.url}


class MossException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnsupportedLanguage(MossException):
    def __init__(self, language, **kwargs):
        super().__init__(f'Unsupported language: {language}', **kwargs)


class MOSS:
    def __init__(self, user_id):
        self.user_id = user_id

    def generate(self, language=DEFAULT_MOSS_LANGUAGE, files=None,
                 base_files=None, is_directory=False, experimental=False,
                 max_matches_until_ignore=MAX_UNTIL_IGNORED, num_to_show=MAX_DISPLAYED_MATCHES, comment='', use_basename=False):
        """Basic interface for generating a report from MOSS"""

        # TODO auto detect language

        # Returns report
        if language not in SUPPORTED_MOSS_LANGUAGES:
            raise UnsupportedLanguage(language)

        url = None
        try:
            moss = MossAPIWrapper(self.user_id)
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

            # Upload base files
            for base_file in base_files:
                moss.upload_base_file(base_file, language, use_basename)

            # Upload submissions
            for index, path in enumerate(files, start=1):
                moss.upload_file(path, language, index, use_basename)

            # Read and return data
            url = moss.generate_url(comment)

            # TODO check for errors
            # b'Error: No files uploaded to compare.\n'

        finally:  # Close session as soon as possible
            moss.close()

        if not url:
            raise MossException('Unable to extract URL')

        return MossResult(url)
