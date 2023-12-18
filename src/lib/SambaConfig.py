import re
import hashlib
import os
import gi


from . import terminal
from gi.repository import GLib  # noqa


from pprint import pprint



class SambaConfig():
    def __init__(self, override_config_file_location=None) -> None:
        flatpak_prefix = '/var/run/host'
        self.config_file_location = '/etc/samba/smb.conf'
        self.tmp_config_file_location = GLib.get_user_cache_dir()

        if os.environ.get('container') == 'flatpak':
            self.config_file_location = flatpak_prefix + self.config_file_location
            # self.tmp_config_file_location = flatpak_prefix + self.tmp_config_file_location

        if override_config_file_location:
            self.config_file_location = override_config_file_location
        
        self.data = {}
        self.original_raw_data = {}

        if os.path.exists(self.config_file_location):
            self._parse()

    def save(self):
        content = []
        for section, data in self.data.items():
            content.append(section)

            for key, value in data.items():
                content.append(self._unparse_key(key) + ' = ' + self._unparse_value(value))

            content.append('\n')
        
        text_content = '\n'.join(content)

        # check file validity
        testfile_path = f'{self.tmp_config_file_location}/simba_smb_validate.conf'
        with open(testfile_path, 'w+') as f:
            f.write(text_content)

        terminal.host_sh(['testparm', '--suppress-prompt', testfile_path])

        terminal.host_sh(['pkexec', 'cp', testfile_path, self.config_file_location])

        if os.path.exists(testfile_path):
            os.remove(testfile_path)

        # backup old file
        
        # request su permission

    def get_md5(self):
        filehash = ''
        
        if os.path.exists(self.config_file_location):
            with open(self.config_file_location, 'rb') as f:
                content = f.read()
                filehash = hashlib.md5(content).hexdigest()

        return filehash

    def get_section(self, section: str) -> dict:
        return self.data.get(f'[{section}]', None)
    
    def create_section(self, section: str, data: dict):
        self.data[f'[{section}]'] = data

    def create_share(self, name: str, share_path: str, writeable: bool, public: bool, comment=''):
        self.create_section(name, {
            'path': share_path,
            'writeable': writeable,
            'public': public,
            'browseable': True,
            'create_mask': '0644', # we manually enforce 0644, default value would be 0755
            'directory_mask': '0755',  # we are just expliciting the permission here, as 0755 is already the default for new directories
            'comment': comment
        })

    def _parse_key(self, key):
        key = key.strip().replace(' ', '_')
        return key
    
    def _unparse_key(self, key):
        key = key.replace('_', ' ')
        return key
    
    def _unparse_value(self, value) -> str:
        if type(value) == bool:
            value = 'yes' if value else 'no'

        value = str(value)
        return value


    def _parse_value(self, value: str):
        parsed_value = value
        parsed_value = parsed_value.strip()

        if value in ['yes', 'no', '1', '0', 'true', 'false']:
            parsed_value = value in ['yes', '1', 'true']

        return parsed_value

    def _parse(self):
        """Parse a smb file"""

        content = ''
        with open(self.config_file_location, 'r') as f:
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
                key = self._parse_key(key)
                parsed_value = self._parse_value(value)

                self.data[curr_section][key] = parsed_value
                self.original_raw_data[curr_section][key] = value
