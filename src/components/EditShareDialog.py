import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from ..lib.SambaConfig import SambaShare

from gi.repository import Gtk, Adw  # noqa


class EditShareDialog():
    def __init__(self, parent, share: SambaShare):
        self.widget = Adw.MessageDialog.new(parent)
        self.widget.set_heading(share.name)

        self.widget.add_response("cancel",  _("_Cancel"))
        self.widget.add_response( "save",    _("_Save"))

        container = Gtk.Box(vexpand=True, orientation=Gtk.Orientation.VERTICAL)
        form = Gtk.ListBox(css_classes=['boxed-list'])

        name_entry = Adw.EntryRow(
            title=_('Name'),
            selectable=False,
            text=share.name
        )

        name_entry.connect('changed', self.on_name_changed)

        desc_entry = Adw.EntryRow(
            title=_('Description'),
            selectable=False,
            text=share.comment
        )
        
        path_entry = Adw.EntryRow(
            title=_('Path'),
            selectable=False,
            text=share.share_path
        )

        [form.append(w) for w in [name_entry, desc_entry, path_entry]]

        container.append(form)
        self.widget.set_extra_child(container)
        self.widget.set_default_size(500, 700)

    def show(self):
        self.widget.show()

    def on_name_changed(self, widget):
        if widget.get_text():
            self.widget.set_heading(widget.get_text())
            self.widget.remove_css_class('dim-heading-dialog')
        else:
            self.widget.set_heading(_('Insert a name'))
            self.widget.add_css_class('dim-heading-dialog')
