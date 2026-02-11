import secrets
import gi
import hashlib
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw  # noqa

def create_boolean_settings_entry(label: str, key: str, subtitle: str = None) -> Adw.ActionRow:
    row = Adw.ActionRow(title=label, subtitle=subtitle)

    switch = Gtk.Switch(valign=Gtk.Align.CENTER)
    self.settings.bind(key, switch, 'active', Gio.SettingsBindFlags.DEFAULT)

    row.add_suffix(switch)
    return row

def get_random_md5():
    # 1. Generate a random string of bytes (16 bytes = 128 bits of entropy)
    random_data = secrets.token_bytes(16)
    
    # 2. Create the MD5 hash object and update it with the random data
    md5_hash = hashlib.md5(random_data).hexdigest()
    
    return md5_hash