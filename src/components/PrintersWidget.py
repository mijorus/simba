import logging
import traceback

import gi

from ..lib.SambaConfig import SambaConfig, SambaUser
from ..lib.HostSystem import HostSystem

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject  # noqa


@Gtk.Template(resource_path='/it/mijorus/simba/ui/printers_widget.ui')
class PrintersWidget(Gtk.Box):
    __gtype_name__ = 'PrintersWidget'

    auth_banner = Gtk.Template.Child()
    enable_print_service = Gtk.Template.Child()
    restrict_access = Gtk.Template.Child()
    allowed_users_group = Gtk.Template.Child()
    add_user_button = Gtk.Template.Child()
    save_button = Gtk.Template.Child()
    not_supported_banner = Gtk.Template.Child()
    pref_widget = Gtk.Template.Child()
    printers_list = Gtk.Template.Child()

    def __init__(self, manager: SambaConfig, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.samba_users: list[SambaUser] = []
        self.allowed_users: list[SambaUser] = []
        self.printer_rows = []
        self.user_rows: list[tuple[SambaUser, Adw.ActionRow]] = []
        self._users_loaded = False
        self._loading = False

        self.restrict_access.connect('notify::active', self._on_restrict_access_toggled)
        self.enable_print_service.connect('notify::active', self._on_enable_service_toggled)
        self.auth_banner.connect('button-clicked', self._on_auth_banner_clicked)
        self.add_user_button.connect('clicked', self._on_add_user_clicked)
        self.save_button.connect('clicked', self._on_save_btn_clicked)

    def reload(self):
        self._loading = True
        self._users_loaded = False
        self.allowed_users = []
        self.save_button.set_sensitive(False)
        self.enable_print_service.set_active(False)
        self.auth_banner.set_revealed(False)
        self.add_user_button.set_sensitive(False)
        self.not_supported_banner.set_revealed(False)
        self.printers_list.set_visible(False)

        for r in self.printer_rows:
            self.printers_list.remove(r)

        self.printer_rows = []

        if self.manager.is_printing_supported():
            self.pref_widget.set_sensitive(True)
            enabled = self.manager.data[self.manager.DEFAULT_SECTION].get('load printers', False)
            self.save_button.set_sensitive(False)
            self.enable_print_service.set_active(enabled)

            if enabled:
                self.printers_list.set_visible(True)

                for p in HostSystem.list_printers():            
                    print_icon = Gtk.Image(icon_name='sb-printer2')
                    printer_row = Adw.ActionRow(title=p)
                    printer_row.add_prefix(print_icon)
                    self.printers_list.add(printer_row)
                    self.printer_rows.append(printer_row)
        else:
            self.pref_widget.set_sensitive(False)
            self.not_supported_banner.set_revealed(True)

        self._loading = False

    def enable_save_button(self):
        if not self._loading:
            self.save_button.set_sensitive(True)

    def _on_save_btn_clicked(self, *args):
        users = None

        if self.restrict_access.get_active():
            users = self.allowed_users

        enabled = self.enable_print_service.get_active()
        self.manager.set_print_service(enabled, restricted_users=users)
        self.manager.save()
        self.reload()

    def _on_enable_service_toggled(self, widget: Adw.SwitchRow, *args):
        self.save_button.set_sensitive(True)

    def _on_restrict_access_toggled(self, switch, _):
        active = switch.get_active()
        self.allowed_users_group.set_visible(active)
        self.enable_save_button()

        if active:
            if not self._users_loaded:
                self.auth_banner.set_revealed(True)
        else:
            self.auth_banner.set_revealed(False)

    def _on_auth_banner_clicked(self, *args):
        try:
            self.samba_users = self.manager.list_users()
        except Exception:
            logging.error(traceback.format_exc())
            return

        self._users_loaded = True
        self.auth_banner.set_revealed(False)
        self.add_user_button.set_sensitive(True)

    def _on_add_user_clicked(self, *args):
        already_allowed = {u.user for u in self.allowed_users}
        available = [u for u in self.samba_users if u.user not in already_allowed]

        if not available:
            return

        dialog = Adw.Dialog(title=_('Add user'), content_width=360)
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(Adw.HeaderBar())

        prefs_page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title=_('Select a user'))

        for user in available:
            row = Adw.ActionRow(
                title=user.user,
                subtitle=user.comment,
                activatable=True,
            )
            row.add_suffix(Gtk.Image.new_from_icon_name('go-next-symbolic'))
            row.connect('activated', lambda _, u=user, d=dialog: self._on_user_selected(u, d))
            group.add(row)

        prefs_page.add(group)
        toolbar_view.set_content(prefs_page)
        dialog.set_child(toolbar_view)

        top_level = Gtk.Window.get_toplevels()[0]
        dialog.present(top_level)

    def _on_user_selected(self, user: SambaUser, dialog: Adw.Dialog):
        dialog.close()
        self.allowed_users.append(user)
        self._add_user_row(user)
        self.enable_save_button()

    def _add_user_row(self, user: SambaUser):
        row = Adw.ActionRow(title=user.user)

        avatar = Adw.Avatar(size=32, text=user.user, show_initials=True)
        row.add_prefix(avatar)

        remove_button = Gtk.Button(
            valign=Gtk.Align.CENTER,
            child=Adw.ButtonContent(
                icon_name='user-trash-symbolic',
                css_classes=['error'],
                label=_('Remove'),
            ),
        )
        remove_button.connect('clicked', lambda _, u=user, r=row: self._on_remove_user(u, r))
        row.add_suffix(remove_button)

        self.allowed_users_group.add(row)
        self.user_rows.append((user, row))

    def _on_remove_user(self, user: SambaUser, row: Adw.ActionRow):
        self.allowed_users = [u for u in self.allowed_users if u.user != user.user]
        self.user_rows = [(u, r) for u, r in self.user_rows if u.user != user.user]
        self.allowed_users_group.remove(row)
        self.enable_save_button()
