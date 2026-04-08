import os
import gi
import traceback
import logging

from ..lib.SambaConfig import SambaShare, SambaConfig, SambaUser
from ..lib.HostSystem import UserAccount
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog
from ..lib.HostSystem import HostSystem
from .UserFormDialog import UserFormDialog


gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw, GObject  # noqa

@Gtk.Template(resource_path='/it/mijorus/simba/ui/userslist.ui')
class UsersList(Gtk.Box):
    __gtype_name__ = 'UsersList'
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    add_button = Gtk.Template.Child()
    banner = Gtk.Template.Child()
    list_widget = Gtk.Template.Child()

    def __init__(self, manager: SambaConfig):
        super().__init__()
        self.manager = manager
        self.user_widgets = []
        self.banner.connect('button_clicked', self.banner_btn_clicked)
        self.add_button.connect('clicked', self.on_add_btn_clicked)
        self.samba_users: list[SambaUser] = []
        self.sys_users: list[UserAccount] = []
        self.list_widget.set_sensitive(False)

    def reload(self):
        pass

    def refresh_users(self):
        for w in self.user_widgets:
            self.list_widget.remove(w)

        for user in self.sys_users:
            found = False

            for suser in self.samba_users:
                if suser.uid == user.uid:
                    found = True
                    break

            if not found:
                continue
            
            user_widget = self.create_user_row(user)
            self.list_widget.add(user_widget)
            self.user_widgets.append(user_widget)

    def banner_btn_clicked(self, *args):
        try:
            self.samba_users = self.manager.list_users()
            self.sys_users = HostSystem.list_users()
        except Exception as e:
            logging.error(traceback.format_exc())
            return

        self.refresh_users()
        self.banner.set_revealed(False)
        self.list_widget.set_sensitive(True)

    def create_user_row(self, user: UserAccount):
        # Create the ActionRow
        user_name = user.username
        comment = user.comment
        row = Adw.ActionRow()

        if comment:
            if comment == HostSystem.MANAGE_USER_PREFIX:
                row.set_title(user_name)
                row.set_subtitle(comment)
            else:
                row.set_title(comment)
                row.set_subtitle(user_name)
        else:
            row.set_title(user_name)

        # 1. Add an Avatar as a Prefix
        avatar = Adw.Avatar(size=32, text=user_name, show_initials=True)

        if user.has_sambashare_group:
            delete_button = Gtk.Button(
                valign=Gtk.Align.CENTER,
                child=Adw.ButtonContent(
                    icon_name='user-trash-symbolic',
                    css_classes=['error'],
                    label=_('Remove')
                )
            )

            delete_button.connect('clicked', 
                                lambda *args: self.on_delete_user_clicked(user))

            row.add_suffix(delete_button)

        row.add_prefix(avatar)
        row.set_activatable(True)
        row.set_selectable(False)

        return row
    
    def on_add_btn_clicked(self, *args):
        top_level = Gtk.Window.get_toplevels()[0]
        form_dialog = UserFormDialog(parent=top_level, samba_users=self.samba_users)
        form_dialog.present()

        form_dialog.connect('save', self.on_new_user_created)

    def on_new_user_created(self, obj, new_user: UserAccount):
        self.sys_users.append(new_user)
        self.samba_users.append(
            SambaUser(user=new_user.username, 
                      uid=new_user.uid, 
                      comment='')
        )

        self.refresh_users()

    def on_delete_user_clicked(self, user: UserAccount):
        pass
        

        # for u in self.sys_users:
        #     if u.username == user_name and u.comment.startswith(HostSystem.MANAGE_USER_PREFIX):
        #         for su in self.samba_users:
        #             if su.user == user_name:
        #                 return

    def on_added_user(self, *args):
        self.refresh_users()