import os
import gi

from .lib.SambaConfig import SambaConfig
from .components.SharedFolders import SharedFolders

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, Adw, GLib  # noqa

class MainWindow(Adw.Window):
    def __init__(self, **kwargs):
        window_title = _('Samba manager')
        super().__init__(
            title=window_title,
            resizable=True, 
            **kwargs
        )

        # Application logic
        self.config_manager = SambaConfig()

        # Gtk stuff
        self.set_default_size(1000, 700)

        shared_folders_widget = SharedFolders(self.config_manager)
        shared_folders_widget.connect('save', self.on_save_btn_clicked)

        view_stack = Adw.ViewStack(margin_top=30)
        view_stack.add_titled_with_icon(shared_folders_widget, 'shared_folders', _('Shared folders'), 'pencil')
        view_stack.add_titled_with_icon(Gtk.Label.new('printers'), 'printers', _('Printers and devices'), 'pencil')
        view_stack.add_titled_with_icon(Gtk.Label.new('settings'), 'settings', _('Preferences'), 'pencil')
        view_stack.set_visible_child(shared_folders_widget)

        view_switcher = Adw.ViewSwitcher(
            stack=view_stack,
            policy=Adw.ViewSwitcherPolicy.WIDE 
        )

        header_bar = Adw.HeaderBar(title_widget=Gtk.Label.new(window_title))
        header_bar.set_title_widget(view_switcher)

        toolbar_view = Adw.ToolbarView(
            content=view_stack
        )

        toolbar_view.add_top_bar(header_bar)

        self.smbconf_filehash = self.config_manager.get_md5()
        print('hash:' + self.smbconf_filehash)

        self.set_content(toolbar_view)


    def on_save_btn_clicked(self, *args):
        self.config_manager.save()
    