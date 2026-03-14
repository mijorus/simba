import secrets
import gi
import hashlib
import os
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw  # noqa

def get_random_md5():
    # 1. Generate a random string of bytes (16 bytes = 128 bits of entropy)
    random_data = secrets.token_bytes(16)
    
    # 2. Create the MD5 hash object and update it with the random data
    md5_hash = hashlib.md5(random_data).hexdigest()
    
    return md5_hash

def mapped_path(path):
    flatpak_prefix = '/run/host'
    if os.environ.get('container') == 'flatpak':
        return flatpak_prefix + path
    
    return path
