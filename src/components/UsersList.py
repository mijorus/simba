import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog
from ..lib.HostSystem import HostSystem

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw, GObject  # noqa


class UsersList(Gtk.Box):
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    def __init__(self, manager: SambaConfig):
        super().__init__()

        self.manager = manager
        self.folder_shares: list[FolderShare] = []

        viewport = Gtk.Viewport.new()
        clamp = Adw.Clamp.new()

        container = Gtk.Box(
            hexpand=True,
            orientation=Gtk.Orientation.VERTICAL
        )

        # self.list_widget = Gtk.FlowBox(
        #     max_children_per_line=1,
        #     selection_mode=Gtk.SelectionMode.NONE,
        #     row_spacing=20,
        # )

        self.list_widget = Adw.PreferencesGroup()
        self.user_widgets = []

        self.banner = Adw.Banner(
            title=_('Users management requires authentication'),
            button_label=_('Unlock'),
            revealed=True
        )

        self.banner.connect('button_clicked', self.banner_btn_clicked)

        btns_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
        )

        add_btn = Gtk.Button(
            css_classes=['flat'],
            child=Adw.ButtonContent(
                icon_name='sb-plus',
                label=_('Add')
            )
        )
        
        # save_btn = Gtk.Button(
        #     css_classes=['suggested-action'],
        #     child=Adw.ButtonContent(
        #         icon_name='sb-checkmark',
        #         label=_('Save')
        #     )
        # )

        btns_row_container = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.END,
            spacing=10,
            hexpand=True,
        )

        add_btn.connect('clicked', self.on_add_btn_clicked)
        # save_btn.connect('clicked', lambda w: self.emit('save', w))
        [btns_row_container.append(w) for w in [
            add_btn,
            # save_btn
        ]]
        
        btns_row.append(btns_row_container)
        container.append(self.banner)

        self.interactive_container = Gtk.Box(
            spacing=30,
            hexpand=True,
            orientation=Gtk.Orientation.VERTICAL
        )

        self.interactive_container.append(btns_row)
        self.interactive_container.append(self.list_widget)
        self.interactive_container.set_sensitive(False)

        container.append(self.interactive_container)

        clamp.set_child(container)
        viewport.set_child(clamp)

        self.append(viewport)

    def refresh_users(self, samba_users, sys_users):
        for w in self.user_widgets:
            self.list_widget.remove(w)

        for user in sys_users:
            found = False

            for suser in samba_users:
                if suser['uid'] == user['uid']:
                    found = True
                    break

            if not found:
                continue

            
            user_widget = self.create_user_row(user['username'], user['comment'])
            self.list_widget.add(user_widget)
            self.user_widgets.append(user_widget)

    def banner_btn_clicked(self, *args):
        samba_users = self.manager.list_users()
        sys_users = HostSystem.list_users()
        self.refresh_users(samba_users, sys_users)
        self.banner.set_revealed(False)
        self.interactive_container.set_sensitive(True)

    def create_user_row(self, user_name, comment=''):
        # Create the ActionRow
        row = Adw.ActionRow()

        if comment:
            row.set_title(comment)
            row.set_subtitle(user_name)
        else:
            row.set_title(user_name)

        # 1. Add an Avatar as a Prefix
        avatar = Adw.Avatar(size=32, text=user_name, show_initials=True)
        row.add_prefix(avatar)

        # # 2. Add a status indicator or button as a Suffix
        # status_label = Gtk.Label(label=user_data["status"])
        # status_label.add_css_class("dim-label") # Standard Adwaita styling
        # row.add_suffix(status_label)
        
        # 3. Add an arrow to indicate it's clickable
        row.set_activatable(True)
        row.set_selectable(False)

        return row
    
    def on_add_btn_clicked(self, *args):
        pass