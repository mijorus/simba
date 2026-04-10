import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw  # noqa


@Gtk.Template(resource_path='/it/mijorus/simba/ui/samba_not_installed.ui')
class SambaNotInstalled(Gtk.Box):
    __gtype_name__ = 'SambaNotInstalled'

    dnf_title = Gtk.Template.Child()
    apt_title = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)