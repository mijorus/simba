import os
import gi

from .lib.SambaConfig import SambaConfig
from .components.SharedFolders import SharedFolders
from .components.UnsupportedConfig import UnsupportedConfig
from .components.Preferences import Preferences
from .components.UsersList import UsersList

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

        # Gtk stuff
        self.set_default_size(1000, 700)

        # Application logic
        self.config_manager = None
        samba_is_compatible = SambaConfig.test_compatibility()
        self.view_stack = None
        self.view_switcher = None
        self.shared_folders_widget = None
        self.unsuppoted_config = UnsupportedConfig()

        header_bar = Adw.HeaderBar(title_widget=Gtk.Label.new(window_title))

        if samba_is_compatible:
            self.config_manager = SambaConfig()

            self.users_list = UsersList(self.config_manager)
            self.shared_folders_widget = SharedFolders(self.config_manager)
            self.preferences_widget = Preferences(self.config_manager)
            self.shared_folders_widget.connect('save', self.on_save_btn_clicked)

            self.view_stack = Adw.ViewStack(margin_top=30)
            self.view_stack.add(self.unsuppoted_config)
            self.view_stack.add_titled_with_icon(self.shared_folders_widget, 'shared_folders', _('Shared folders'), 'pencil')
            self.view_stack.add_titled_with_icon(self.users_list, 'users_list', _('Users list'), 'pencil')
            self.view_stack.add_titled_with_icon(Gtk.Label.new('printers'), 'printers', _('Printers and devices'), 'pencil')
            self.view_stack.add_titled_with_icon(self.preferences_widget, 'settings', _('Preferences'), 'pencil')
            self.view_switcher = Adw.ViewSwitcher(
                stack=self.view_stack,
                policy=Adw.ViewSwitcherPolicy.WIDE 
            )

            if self.config_manager.is_config_supported():
                self.view_stack.set_visible_child(self.shared_folders_widget)
            else:
                self.view_stack.set_visible_child(self.unsuppoted_config)
                self.view_switcher.set_sensitive(False)
                self.unsuppoted_config.connect('fix_button_clicked', self.on_fix_btn_clicked)


            header_bar.set_title_widget(self.view_switcher)

            toolbar_view = Adw.ToolbarView(
                content=self.view_stack
            )

            toolbar_view.add_top_bar(header_bar)
            self.set_content(toolbar_view)
        else:
            toolbar_view = Adw.ToolbarView(
                content=Gtk.Label.new('Samba is not installed')
            )

            toolbar_view.add_top_bar(header_bar)

            self.set_content(toolbar_view)


    def on_save_btn_clicked(self, *args):
        if self.config_manager:
            self.config_manager.save()

    def refresh_valid_config(self):
        if self.config_manager and self.view_stack and self.view_switcher:
            if self.config_manager.is_config_supported():
                self.view_stack.set_visible_child(self.shared_folders_widget)
                self.view_switcher.set_sensitive(True)
            else:
                self.view_switcher.set_sensitive(False)
                self.view_stack.set_visible_child(self.unsuppoted_config)

    
    def on_fix_btn_clicked(self, *args):
        if self.config_manager:
            self.config_manager.init_with_defaults()
            self.config_manager.save()
            self.refresh_valid_config()