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

    workgroup_row = Gtk.Template.Child()
    logfile_row = Gtk.Template.Child()
    usershare_max_shares_row = Gtk.Template.Child()
    usershare_enabled = Gtk.Template.Child()

    def __init__(self, manager: SambaConfig, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.workgroup_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('workgroup', ''))
        self.logfile_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('log file', ''))
        self.usershare_max_shares_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('usershare max shares', '0'))
        self.usershare_enabled.set_active(self.manager.data.has_option(SambaConfig.DEFAULT_SECTION, 'usershare path'))

        self.usershare_max_shares_row.set_range(1, 10)
        