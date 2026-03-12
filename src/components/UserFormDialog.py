import gi
import re
import logging
import traceback

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject

from .FormRow import FormRow
from ..lib.HostSystem import HostSystem
from ..lib.SambaConfig import SambaConfig, SambaUser

class UserFormDialog(Adw.MessageDialog):
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_OBJECT, (object, )),
    }

    def __init__(self, parent, samba_users: list[SambaUser]):
        super().__init__(
            transient_for=parent,
            heading=_("Add user"),
            resizable=True,
        )

        self.set_default_size(400, 400)
        samba_usernames = [u.user for u in samba_users]

        users_list = []
        for u in HostSystem.list_users():
            if (u.is_system_user == False) and (not u.is_nologin) \
                and (u.username not in samba_usernames):
                users_list.append(u.username)

        self.toggle_group = Adw.ToggleGroup(css_classes=['round'])
        self.toggle_group.add(Adw.Toggle(label=_('New user'), name='new'))

        if users_list:
            self.toggle_group.add(Adw.Toggle(label=_('Existing system user'), name='existing'))

        self.toggle_group.set_active_name('new')
        self.toggle_group.connect('notify::active-name', self.switch_user_type)

        form_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, spacing=20)

        users_model = Gtk.StringList.new(users_list)

        # Create a form for a new user
        self.form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        form_container.append(self.toggle_group)
        form_container.append(self.form)

        # Create a combo row for users
        combo_row_container = Gtk.ListBox(css_classes=['boxed-list'])
        self.combo_row = Adw.ComboRow(title=_("Select a user"), model=users_model, visible=False)
        combo_row_container.append(self.combo_row)

        self.form.append(combo_row_container)

        # 2. Add Username Row
        self.username_row = FormRow(
            name='username',
            title='User Name',
            text='',
            max_length=32,
            valitator=self.username_validator,
            after_validation=self.check_form_is_valid,
            description=_('The name of the new system user that will be created, only letters and numbers are accepted')
        )

        self.form.append(self.username_row)
        self.username_row.validator = self.username_validator

        # 3. Add Full Name Row
        self.fullname_row = FormRow(
            name='full_name',
            title='Full Name',
            text='',
            max_length=32,
            description=_('The full name of the new user')
        )

        self.sys_users = HostSystem.list_users()

        self.form.append(self.fullname_row)

        self.pwd_row = FormRow(
            name='pwd',
            title='SMB Password',
            is_passwd=True,
            text='',
            valitator=self.pwd_validator,
            after_validation=self.check_form_is_valid,
        )

        self.pwd_row.set_margin_top(20)

        self.pwd_confirm_row = FormRow(
            name='pwd_confirm',
            is_passwd=True,
            title=_('Password confirm'),
            text='',
            valitator=self.pwd_validator,
            after_validation=self.check_form_is_valid
        )

        self.form.append(self.pwd_row)
        self.form.append(self.pwd_confirm_row)

        # Set the list_box as the extra child of the MessageDialog
        self.set_extra_child(form_container)

        # 4. Add Buttons (Responses)
        self.add_response("cancel", _("Cancel"))
        self.add_response("save", _("Save"))
        
        # Set 'Save' as the suggested action (colored button)
        self.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
        self.set_response_appearance("cancel", Adw.ResponseAppearance.DESTRUCTIVE)
        self.set_response_enabled('save', False)

        # Connect the response signal
        self.connect("response", self.on_response)
        self.form_is_valid = False

    def on_response(self, dialog, response):
        if response == "save":
            a = self.toggle_group.get_active_name()
            pwd = self.pwd_row.entry.get_text()
            pwd_check = self.pwd_confirm_row.entry.get_text()

            if pwd != pwd_check:
                raise Exception('Password and Password check are different')

            if a == 'new':
                usn = self.username_row.entry.get_text()
                fnm = self.fullname_row.entry.get_text()

                try:
                    new_user = HostSystem.create_system_and_samba_user(usn, fnm, pwd)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    return
            else:
                selected_username = self.combo_row.get_model().get_item(self.combo_row.get_selected()).get_string()

                try:
                    SambaConfig.create_user(user=selected_username, passwd=pwd)
                    new_user = HostSystem.get_user(selected_username)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    return

            self.emit('save', new_user)

    def check_form_is_valid(self):
        active_usertype = self.toggle_group.get_active_name()

        if active_usertype == 'new':
            self.form_is_valid = all([w._is_valid for w in [
                    self.username_row, self.fullname_row, self.pwd_row, self.pwd_confirm_row]])
        else:
            self.form_is_valid = all([w._is_valid for w in [self.pwd_row, self.pwd_confirm_row]])

        self.set_response_enabled('save', self.form_is_valid)

    def username_validator(self, name, text) -> bool:
        if not text:
            return False

        for u in self.sys_users:
            if u.username == text:
                return False
            
        pattern = r"^[a-z0-9-_]+$"

        if not re.match(pattern, text):
            return False
        
        return True
    
    def pwd_validator(self, name, text) -> bool:
        if len(text) < 5:
            return False
        
        if name == 'pwd_confirm':
            return text == self.pwd_row.entry.get_text()
        
        return True
    
    def switch_user_type(self, *args):
        name = self.toggle_group.get_active_name()
        self.username_row.set_visible(name == 'new')
        self.fullname_row.set_visible(name == 'new')
        self.combo_row.set_visible(name == 'existing')
        self.check_form_is_valid()
