import gi
import re
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject

from .FormRow import FormRow
from ..lib.HostSystem import HostSystem

class UserFormDialog(Adw.Dialog):
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_OBJECT, (object, )),
    }

    def __init__(self, parent):
        super().__init__(
            # transient_for=parent,
            title=_("Add user"),
            # reskizable=True,
        )

        # self.set_default_size(400, 400)

        # 1. Create the Form Container
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # 2. Add Username Row
        self.username_row = FormRow(
            name='username',
            title='User Name',
            text='',
            max_length=32,
            description=_('The name of the new system user that will be created, only letters and numbers are accepted')
        )

        form.append(self.username_row)
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

        form.append(self.fullname_row)

        self.pwd_row = FormRow(
            name='pwd',
            title='Password',
            text='',
            valitator=self.pwd_validator
        )

        self.set_margin_top(20)

        self.pwd_confirm_row = FormRow(
            name='pwd_confirm',
            title=_('Password confirm'),
            text='',
            valitator=self.pwd_validator
        )

        form.append(self.pwd_row)
        form.append(self.pwd_confirm_row)

        # Set the list_box as the extra child of the MessageDialog
        self.set_child(form)

        # 4. Add Buttons (Responses)
        # self.add_response("cancel", _("Cancel"))
        # self.add_response("save", _("Save"))
        
        # # Set 'Save' as the suggested action (colored button)
        # self.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
        # self.set_response_appearance("cancel", Adw.ResponseAppearance.DESTRUCTIVE)
        
        # # Connect the response signal
        # self.connect("response", self.on_response)

    def on_response(self, dialog, response):
        if response == "save":
            valid = all([w._is_valid for w in [
                self.username_row, self.fullname_row, self.pwd_row, self.pwd_confirm_row]])

            if valid:
                usn = self.username_row.entry.get_text()
                fnm = self.fullname_row.entry.get_text()
                pwd = self.pwd_row.entry.get_text()
                new_user = HostSystem.create_system_and_samba_user(usn, fnm, pwd)
                if new_user:
                    pass

                self.emit('save', None)
                return True
            return False
        else:
            return True

    def username_validator(self, name, text) -> bool:
        if not text:
            return False

        for u in self.sys_users:
            if u['username'] == text:
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