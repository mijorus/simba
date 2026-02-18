import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject  # noqa


@Gtk.Template(resource_path='/it/mijorus/simba/ui/preferences.ui')
class Preferences(Gtk.Box):
    __gtype_name__ = 'Preferences'
    __gsignals__ = {
        # 'fix_button_clicked': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, manager: SambaConfig, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.workgroup_row = Gtk.Template.Child()
        self.logifile_row = Gtk.Template.Child()