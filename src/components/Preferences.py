import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from ..lib.HostSystem import HostSystem, NetworkName
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
    allow_only_toggle = Gtk.Template.Child()
    allow_networks = Gtk.Template.Child()
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
        self.allow_networks_rows: list[tuple[NetworkName, Adw.SwitchRow,]] = []

        if HostSystem.has_network_manager():
            networks = HostSystem.list_saved_networks()
            enabled_networks = self.manager.get_nm_allowed_networks()
            print(enabled_networks)

            for n in networks:
                row = Adw.SwitchRow(title=n.name, subtitle=n._type.capitalize())
                row.set_active(n.uuid in enabled_networks)
                self.allow_networks.add_row(row)
                self.allow_networks_rows.append((n, row))

            self.allow_only_toggle.set_sensitive(True)
            self.allow_only_toggle.set_active(self.manager.has_toggle_script())
            self.allow_networks.set_sensitive(self.allow_only_toggle.get_active())
            self.allow_only_toggle.connect('notify::active', lambda w, _: self.allow_networks.set_sensitive(w.get_active()))

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

        allow_networks = None
        if HostSystem.has_network_manager():
            if self.allow_only_toggle.get_active():
                allow_networks = []
                for n in self.allow_networks_rows:
                    if n[1].get_active():
                        allow_networks.append(n[0])

        self.manager.save(
            allowed_networks=allow_networks
        )
