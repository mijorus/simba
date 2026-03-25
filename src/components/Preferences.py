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
    netbios_row = Gtk.Template.Child()
    logfile_row = Gtk.Template.Child()
    usershare_max_shares_row = Gtk.Template.Child()
    usershare_enabled = Gtk.Template.Child()
    save_button = Gtk.Template.Child()

    def __init__(self, manager: SambaConfig, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.workgroup_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('workgroup', ''))
        self.netbios_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('netbios name', ''))
        self.logfile_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('log file', ''))
        self.usershare_max_shares_row.set_text(self.manager.data[SambaConfig.DEFAULT_SECTION].get('usershare max shares', '1'))
        self.usershare_enabled.set_active(self.manager.data.has_option(SambaConfig.DEFAULT_SECTION, 'usershare path'))

        self.usershare_max_shares_row.set_sensitive(self.usershare_enabled.get_active())
        self.usershare_enabled.connect('notify::active', lambda w, _: self.usershare_max_shares_row.set_sensitive(w.get_active()))

        self.save_button.connect('clicked', self.on_save_clicked)

    def on_save_clicked(self, *args):
        section = self.manager.data[self.manager.DEFAULT_SECTION]
        section['workgroup'] = self.workgroup_row.get_text()
        section['netbios name'] = self.netbios_row.get_text()

        if self.usershare_enabled.get_active():
            section['usershare max shares'] = str(int(self.usershare_max_shares_row.get_value()))
            section['usershare path'] = section.get('usershare path', '')
        else:
            if 'usershare path' in section:
                del section['usershare path']
            if 'usershare max shares' in section:
                del section['usershare max shares']

        self.manager.save()
