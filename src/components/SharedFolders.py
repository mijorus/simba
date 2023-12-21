import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw  # noqa


class SharedFolders(Gtk.Box):
    def __init__(self, shares: list[SambaShare], manager=SambaConfig):
        super().__init__()

        self.manager = manager

        viewport = Gtk.Viewport.new()
        clamp = Adw.Clamp.new()
        list_widget = Gtk.Box(
            spacing=45,
            orientation=Gtk.Orientation.VERTICAL
        )

        btns_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        add_btn = Gtk.Button(
            child=Adw.ButtonContent(
                icon_name='pencil-symbolic',
                label=_('Save')
            )
        )

        add_btn.connect('clicked', self.on_save_btn_clicked)
        btns_row.append(add_btn)
        list_widget.append(btns_row)

        for share in shares:
            list_widget.append(FolderShare(share))

        clamp.set_child(list_widget)
        viewport.set_child(clamp)

        self.append(viewport)

    def on_save_btn_clicked(self, widget: Gtk.Button):
        self.manager.save()