import re
import os
import gi
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from ..lib.SambaConfig import SambaShare

from gi.repository import Gtk, Adw, GObject  # noqa


class FormRow(Gtk.Box):
    def __init__(self, name: str, title: str, text: str, max_length=100, description: str='', valitator: callable=None) -> None:
        """
            validator: The validator function should return False if the string is not valid
        """
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            margin_bottom=10
        )

        self._is_valid = True
        self.max_length = max_length
        self.name = name

        container = Gtk.ListBox(css_classes=['boxed-list'])

        self.entry = Adw.EntryRow(
            title=title,
            text=text,
            enable_emoji_completion=False
        )

        self.entry.get_delegate().set_max_length(max_length)

        self.validator = valitator
        self.entry.connect('changed', self.on_entry_changed)

        desc = Gtk.Label(
            label=description + ' (max. {max_char} characters)'.format(max_char=max_length),
            halign=Gtk.Align.START,
            css_classes=['dim-label', 'toolbar', 'caption']
        )

        container.append(self.entry)

        self.append(container)
        self.append(desc)

    
    def on_entry_changed(self, widget):
        if self.validator:
            self._is_valid = self.validator(self.name, widget.get_text())

            if not self._is_valid:
                widget.add_css_class('error')
            else:
                widget.remove_css_class('error')

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
            valitator=self.form_validator
        )

        self.name_entry.entry.connect('changed', self.on_name_changed)

        self.desc_entry = FormRow(
            name='description',
            title=_('Description'),
            text=share.comment,
            max_length=100,
            description=_('Additional information that might be helpful to identify this share'),
            valitator=self.form_validator
        )

        self.path_entry = Adw.EntryRow(
            title=_('Path'),
            text=share.share_path,
            enable_emoji_completion=False
        )

        select_path_btn = Gtk.Button(icon_name='folder-symbolic', valign=Gtk.Align.CENTER)
        select_path_btn.connect('clicked', self.on_select_path_btn_clicked)
        self.path_entry.add_suffix(select_path_btn)
        
        form_container = FormContainer()
        form_container.append(self.path_entry)

        readonly_row = Adw.ActionRow(
            title=_('Read only'),
            subtitle=_('When a share is set as read-only, clients will not be able to modify, create or delete files')
        )

        self.readonly_switch = Gtk.Switch(valign=Gtk.Align.CENTER, active=(share.writeable == False))
        readonly_row.add_suffix(self.readonly_switch)
        form_container.append(readonly_row)

        [form.append(w) for w in [
            self.name_entry, 
            self.desc_entry, 
            form_container,
        ]]

        container.append(form)
        self.widget.set_extra_child(container)
        self.widget.set_default_size(500, 700)

    def name_entry_validator(self, text: str) -> bool:
        is_valid = text == re.sub(r'[^a-zA-Z0-9\_\-]', '', text)
        return is_valid

    def desc_entry_validator(self, text: str) -> bool:
        is_valid = text == re.sub(r'[^0-9a-zA-ZÀ-ú\-\_\s]', '', text)
        return is_valid

    def form_validator(self, entry_name: str, text: str) -> bool:
        is_valid = False

        if entry_name == 'name':
            is_valid = text == re.sub(r'[^a-zA-Z0-9\_\-]', '', text)
        elif entry_name == 'description':
            is_valid = text == re.sub(r'[^0-9a-zA-ZÀ-ú\-\_\s]', '', text)


        if is_valid:
            self.valid_form = True

            validate_not_empty = [
                self.name_entry.entry.get_text(), 
                self.path_entry.get_text()
            ]
            
            for entry in validate_not_empty:
                if not entry:
                    self.valid_form = False
        else:
            self.valid_form = False

        if not self.valid_form:
            pass
            #TODO

        return is_valid
        

    def show(self):
        self.widget.show()

    def on_name_changed(self, widget):
        # if widget.get_text():
        #     self.widget.set_heading(widget.get_text())
        #     self.widget.remove_css_class('dim-heading-dialog')
        # else:
        #     self.widget.set_heading(_('Insert a name'))
        #     self.widget.add_css_class('dim-heading-dialog')

        pass

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
        
        self.path_entry.set_text(selected_path)
        self.share.share_path = selected_path

    def on_dialog_response(self, widget, response: str):
        if response == 'save':
            for entry in [self.name_entry, self.desc_entry]:
                if not entry._is_valid:
                    return
                
            validate_not_empty = [
                self.name_entry.entry.get_text(), 
                self.path_entry.get_text(),
            ]
            
            for entry in validate_not_empty:
                if not entry:
                    return

            self.share.name = self.name_entry.entry.get_text()
            self.share.comment = self.desc_entry.entry.get_text()
            self.share.writeable = self.readonly_switch.get_active()

            self.emit('save', self.share)

GObject.type_register(EditShareDialog)