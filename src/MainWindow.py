import os
import gi

from .lib.SambaConfig import SambaConfig
from .components.SharedFolders import SharedFolders

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, Adw, GLib  # noqa

class MainWindow(Gtk.ApplicationWindow):
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

        header_bar = Adw.HeaderBar(title_widget=Gtk.Label.new(window_title))
        save_btn = Gtk.Button(
            # sensitive=False,
            css_classes=['raised'],
            child=Adw.ButtonContent(
                icon_name='checkmark-symbolic',
                label=_('Apply')
            )
        )

        save_btn.connect('clicked', self.on_save_btn_clicked)

        header_bar.pack_end(save_btn)
        self.set_titlebar(header_bar)

        view_stack = Gtk.Stack(margin_top=30)
        view_stack.add_titled(SharedFolders(self.config_manager), 'shared_folders', _('Shared folders'))
        view_stack.add_titled(Gtk.Label.new('printers'), 'printers', _('Printers and devices'))
        view_stack.add_titled(Gtk.Label.new('settings'), 'settings', _('Preferences'))

        stack_sidebar = Gtk.StackSidebar(stack=view_stack)
        navigation_splitview = Adw.NavigationSplitView(
            sidebar=Adw.NavigationPage(child=stack_sidebar, title='test'),
            content=Adw.NavigationPage(child=view_stack, title='test')
        )

        self.smbconf_filehash = self.config_manager.get_md5()
        print('hash:' + self.smbconf_filehash)

        self.set_child(navigation_splitview)


    def on_save_btn_clicked(self, widget):
        self.config_manager.save()
    