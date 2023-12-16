import re
import hashlib
import os
from pprint import pprint

DEFAULT_SMB_FILE_LOCATION = '/etc/samba/smb.conf'

if os.environ.get('container') == 'flatpak':
    DEFAULT_SMB_FILE_LOCATION = '/var/run/host' + DEFAULT_SMB_FILE_LOCATION

class SambaConfig():
    def __init__(self) -> None:
        self.data = {}
        self.original_raw_data = {}

    def get_md5(file_path=DEFAULT_SMB_FILE_LOCATION):
        filehash = ''
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
                filehash = hashlib.md5(content).hexdigest()

        return filehash

    def get_section(self, section: str) -> dict:
        return self.data.get(f'[{section}]', None)
    
    def create_section(self, section: str):
        self.data[f'[{section}]'] = {}

    def parse(self, file_path=DEFAULT_SMB_FILE_LOCATION):
        """Parse a smb file"""

        content = ''
        with open(file_path, 'r') as f:
            content = f.read()

        lines = content.split('\n')
        section_re = re.compile(r'\[(.*)\]')
        self.data = {}

        curr_section = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue

            if section_re.match(line):
                self.data[line] = {}
                self.original_raw_data[line] = {}
                curr_section = line

            else:
                key, value = line.split('=', 1)
                key = key.strip().replace(' ', '_')
                value = value.strip()

                parsed_value = value

                if value in ['yes', 'no', '1', '0', 'true', 'false']:
                    parsed_value = value in ['yes', '1', 'true']

                self.data[curr_section][key] = parsed_value
                self.original_raw_data[curr_section][key] = value
