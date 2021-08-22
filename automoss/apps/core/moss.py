import socket
import os
import re


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
        self._send_string(f'language {language}')

    def upload_base_file(self, file_path, language):
        self.upload_file(file_path, language, 0)

    def upload_file(self, file_path, language, file_id):
        # TODO remove language param?
        if not os.path.exists(file_path):
            raise FileNotFoundError  # File does not exist

        size = os.path.getsize(file_path)

        # Replace whitespace with _
        file_name = re.sub('\s+', '_', file_path).replace('\\', '/')

        # Send file header information
        self._send_string(f'file {file_id} {language} {size} {file_name}')

        # Send actual file info
        with open(file_path, 'rb') as f:
            self._send_raw(f.read())

    def generate_url(self, comment=''):
        # Send final query
        self._send_string(f'query 0 {comment}')
        return self.read()

    def _send_raw(self, bytes):
        self.socket.send(bytes)

    def _send_string(self, text):
        return self._send_raw(f'{text}\n'.encode())
