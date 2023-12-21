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


    def show(self):
        self.widget.show()