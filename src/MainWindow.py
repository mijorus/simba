import os
import gi

from time import sleep
from .lib.SambaConfig import SambaConfig
from .components.SharedFolders import SharedFolders
from .components.UnsupportedConfig import UnsupportedConfig
from .components.Preferences import Preferences
from .components.UsersList import UsersList
from .components.PrintersWidget import PrintersWidget
from .components.Warnings import Warnings
from .components.SambaNotInstalled import SambaNotInstalled
from .lib import async_utils

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, Adw, GLib  # noqa

class MainWindow(Adw.Window):
    def __init__(self, **kwargs):
        window_title = _('Simba')
        super().__init__(
            # title=window_title,
            resizable=True, 
            **kwargs
        )

        # Gtk stuff
        self.set_default_size(1000, 700)

        # Application logic
        self.config_manager = None
        samba_is_compatible = SambaConfig.test_compatibility()
        self.view_stack = None
        self.sidebar_list = None
        self.shared_folders_widget = None
        self.unsuppoted_config = UnsupportedConfig()

        if samba_is_compatible:
            self.config_manager = SambaConfig()

            self.users_list = UsersList(self.config_manager)
            self.shared_folders_widget = SharedFolders(self.config_manager)
            self.preferences_widget = Preferences(self.config_manager)
            self.printers_widget = PrintersWidget(self.config_manager)
            self.warnings_widget = Warnings(self.config_manager)

            pages = [
                (self.shared_folders_widget, 'shared_folders', _('Shared folders'), 'sb-folder-remote'),
                (self.users_list, 'users_list', _('Users list'), 'sb-people'),
                (self.printers_widget, 'printers', _('Printers and devices'), 'sb-printer2'),
                (self.preferences_widget, 'settings', _('Preferences'), 'sb-settings'),
            ]

            if self.warnings_widget._warnings:
                wt = _('Warnings') + f' ({len(self.warnings_widget._warnings)})'
                pages.append((self.warnings_widget, 'warnings', wt, 'dialog-warning-symbolic'))

            self.view_stack = Adw.ViewStack(hexpand=True, vexpand=True)
            self.view_stack.connect('notify::visible-child', self.on_view_stack_visible_child_changed)
            self.view_stack.add(self.unsuppoted_config)
            for widget, name, label, icon in pages:
                self.view_stack.add_titled_with_icon(widget, name, label, icon)

            self.sidebar_list = Gtk.ListBox(
                selection_mode=Gtk.SelectionMode.SINGLE,
                css_classes=['navigation-sidebar'],
                vexpand=True,
            )

            for w, name, label, icon in pages:
                row = Adw.ActionRow(title=label, activatable=True, name=name)
                row.add_prefix(Gtk.Image.new_from_icon_name(icon))
                self.sidebar_list.append(row)
            self.sidebar_list.connect('row-activated', self.on_sidebar_row_activated)

            if self.config_manager.is_config_supported():
                self.view_stack.set_visible_child(self.shared_folders_widget)
                self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
            else:
                self.view_stack.set_visible_child(self.unsuppoted_config)
                self.sidebar_list.set_sensitive(False)
                self.unsuppoted_config.connect('fix_button_clicked', self.on_fix_btn_clicked)

            self.service_status_dot = Gtk.Label(label='●', css_classes=['service-status-dot'])
            self.service_status_label = Gtk.Label(label='', xalign=0)

            status_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=8,
                margin_start=12, margin_end=12,
                margin_top=10, margin_bottom=10,
            )
            status_box.append(self.service_status_dot)
            status_box.append(self.service_status_label)

            sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            sidebar_box.append(self.sidebar_list)
            sidebar_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
            sidebar_box.append(status_box)

            sidebar_toolbar = Adw.ToolbarView(content=sidebar_box)
            sidebar_toolbar.add_top_bar(Adw.HeaderBar(
                title_widget=Gtk.Label.new(window_title)
            ))

            content_toolbar = Adw.ToolbarView(content=self.view_stack)
            content_toolbar.add_top_bar(Adw.HeaderBar())

            split_view = Adw.NavigationSplitView(
                sidebar=Adw.NavigationPage(
                    title=window_title,
                    child=sidebar_toolbar,
                ),
                content=Adw.NavigationPage(
                    child=content_toolbar,
                ),
            )

            self.start_sambad_check()
            self.set_content(split_view)
        else:
            toolbar_view = Adw.ToolbarView(
                content=SambaNotInstalled()
            )
            toolbar_view.add_top_bar(Adw.HeaderBar(
                title_widget=Gtk.Label.new(window_title)
            ))
            self.set_content(toolbar_view)

    def on_view_stack_visible_child_changed(self, *args):
        child = self.view_stack.get_visible_child()
            
        if hasattr(child, 'reload') and self.config_manager:
            self.config_manager.reload()
            child.reload() # type: ignore


    def on_sidebar_row_activated(self, listbox, row):
        if not self.view_stack:
            return

        child = self.view_stack.get_child_by_name(row.get_name())

        if child:
            self.view_stack.set_visible_child(child)

    @async_utils._async
    def start_sambad_check(self):
        while self.config_manager:
            self.refresh_sambad_status()
            sleep(3)

    @async_utils.idle
    def refresh_sambad_status(self):
        if self.config_manager:
            if self.config_manager.is_service_active():
                self.service_status_label.set_text(_('Service is running'))
                self.service_status_dot.set_css_classes(['service-status-dot', 'active'])
            else:
                self.service_status_label.set_text(_('Service is not running'))
                self.service_status_dot.set_css_classes(['service-status-dot'])

    def refresh_valid_config(self):
        if self.config_manager and self.view_stack and self.sidebar_list:
            if self.config_manager.is_config_supported():
                self.view_stack.set_visible_child(self.shared_folders_widget)
                self.sidebar_list.set_sensitive(True)
                self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
            else:
                self.sidebar_list.set_sensitive(False)
                self.view_stack.set_visible_child(self.unsuppoted_config)

    
    def on_fix_btn_clicked(self, *args):
        if self.config_manager:
            self.config_manager.init_with_defaults()
            self.config_manager.save()
            self.refresh_valid_config()