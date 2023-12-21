import os
import gi
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