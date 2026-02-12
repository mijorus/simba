import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject  # noqa


@Gtk.Template(resource_path='/it/mijorus/simba/ui/unsupported_config.ui')
class UnsupportedConfig(Gtk.Box):
    __gtype_name__ = 'UnsupportedConfig'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)