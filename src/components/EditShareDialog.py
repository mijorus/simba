import re
import os
import gi
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from ..lib.SambaConfig import SambaShare
from .FormRow import FormRow
from gi.repository import Gtk, Adw, GObject  # noqa

class FormContainer(Gtk.ListBox):
    def __init__(self) -> None:
        super().__init__(
            css_classes=['boxed-list'],
            # orientation=Gtk.Orientation.VERTICAL,
            margin_bottom=10
        )

class EditShareDialog(GObject.GObject):
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    def __init__(self, parent, share: SambaShare, new_share=False):
        super().__init__()

        self.share = share
        self.widget = Adw.MessageDialog.new(parent)
        self.widget.set_heading(_('Create share') if new_share else _('Edit share'))
        self.widget.set_resizable(True)
        self.valid_form = False

        self.widget.add_response("cancel",  _("_Cancel"))
        self.widget.add_response( "save",    _("_Save"))

        self.widget.set_response_appearance('cancel', Adw.ResponseAppearance.DESTRUCTIVE)
        self.widget.set_response_appearance('save', Adw.ResponseAppearance.SUGGESTED)

        self.widget.connect('response', self.on_dialog_response)

        container = Gtk.Box(vexpand=True, orientation=Gtk.Orientation.VERTICAL)
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.name_entry = FormRow(
            name='name',
            title=_('Name'), 
            text=share.name,
            description=_('How share will be visible on the network. Only numbers, letters and dashes are allowed'),
            max_length=8,
            min_length=3,
            validator=self.name_entry_validator,
            after_validation=self.after_validation,
        )

        self.desc_entry = FormRow(
            name='description',
            title=_('Description'),
            text=share.comment,
            max_length=100,
            description=_('Additional information that might be helpful to identify this share'),
            validator=self.desc_entry_validator,
            after_validation=self.after_validation
        )

        self.path_entry = FormRow(
            name='path',
            title=_('Path'),
            text=share.share_path,
            show_constrains=False,
            min_length=1,
        )

        select_path_btn = Gtk.Button(icon_name='sb-folder-symbolic', valign=Gtk.Align.CENTER)
        select_path_btn.connect('clicked', self.on_select_path_btn_clicked)
        self.path_entry.entry.add_suffix(select_path_btn)
        
        readonly_row_container = Gtk.ListBox(css_classes=['boxed-list'])
        self.readonly_row = Adw.SwitchRow(
            title=_('Read only'),
            subtitle=_('When a share is set as read-only, clients will not be able to modify, create or delete files'),
            active=(share.writeable == False),
        )

        readonly_row_container.append(self.readonly_row)

        [form.append(w) for w in [
            self.name_entry, 
            self.desc_entry, 
            self.path_entry,
            readonly_row_container,
        ]]

        self.after_validation()

        container.append(form)
        self.widget.set_extra_child(container)
        self.widget.set_default_size(500, 700)

    def name_entry_validator(self, name, text: str) -> bool:
        is_valid = text == re.sub(r'[^a-zA-Z0-9\_\-]', '', text)
        return is_valid

    def desc_entry_validator(self, name, text: str) -> bool:
        is_valid = text == re.sub(r'[^0-9a-zA-ZÀ-ú\-\_\s]', '', text)
        return is_valid

    # def form_validator(self, entry_name: str, text: str) -> bool:
    #     is_valid = False

    #     if entry_name == 'name':
    #         is_valid = text == re.sub(r'[^a-zA-Z0-9\_\-]', '', text)
    #     elif entry_name == 'description':
    #         is_valid = text == re.sub(r'[^0-9a-zA-ZÀ-ú\-\_\s]', '', text)


    #     if is_valid:
    #         self.valid_form = True

    #         validate_not_empty = [
    #             self.name_entry.entry.get_text(), 
    #             self.path_entry.get_text()
    #         ]
            
    #         for entry in validate_not_empty:
    #             if not entry:
    #                 self.valid_form = False
    #     else:
    #         self.valid_form = False

    #     if not self.valid_form:
    #         pass
    #         #TODO

    #     return is_valid
    def after_validation(self):
        self.valid_form = all([w._is_valid for w in [
                    self.desc_entry, self.name_entry, self.path_entry]])
        
        self.widget.set_response_enabled('save', self.valid_form)

    def show(self):
        self.widget.show()

    def on_select_path_btn_clicked(self, widget):
        dialog = Gtk.FileDialog(title=_('Select a folder'), modal=True)
        top_level = Gtk.Window.get_toplevels()[0]

        dialog.select_folder(
            parent=top_level,
            cancellable=None,
            callback=self.on_select_path_response
        )

    def on_select_path_response(self, dialog, result):
        selected_path = None
        
        try:
            selected_gfile = dialog.select_folder_finish(result)
            selected_path = selected_gfile.get_path()
        except Exception as e:
            logging.error(str(e))
            return
        
        self.path_entry.entry.set_text(selected_path)
        self.share.share_path = selected_path

    def on_dialog_response(self, widget, response: str):
        if response == 'save':
            if not self.valid_form:
                raise Exception('Form is not valid')

            self.share.name = self.name_entry.entry.get_text()
            self.share.comment = self.desc_entry.entry.get_text()
            self.share.writeable = (not self.readonly_row.get_active())

            self.emit('save', self.share)

GObject.type_register(EditShareDialog)