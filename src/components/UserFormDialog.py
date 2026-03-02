import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject

from .FormRow import FormRow

class UserFormDialog(Adw.MessageDialog):
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    def __init__(self, parent):
        super().__init__(
            transient_for=parent,
            heading=_("Add user"),
            resizable=True,
        )

        self.set_default_size(500, 400)

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

        # 3. Add Full Name Row
        self.fullname_row = FormRow(
            name='full_name',
            title='Full Name',
            text='',
            max_length=32,
            description=_('The full name of the new user')
        )

        form.append(self.fullname_row)

        # Set the list_box as the extra child of the MessageDialog
        self.set_extra_child(form)

        # 4. Add Buttons (Responses)
        self.add_response("cancel", "Cancel")
        self.add_response("save", "Save")
        
        # Set 'Save' as the suggested action (colored button)
        self.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
        self.set_response_appearance("cancel", Adw.ResponseAppearance.DESTRUCTIVE)
        
        # Connect the response signal
        self.connect("response", self.on_response)

    def on_response(self, dialog, response):
        if response == "save":
            valid = all([w._is_valid for w in [self.username_row, self.fullname_row]])
            if valid:
                self.emit('save', None)
        
        self.destroy()