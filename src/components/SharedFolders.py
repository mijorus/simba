import os
import gi

from ..lib.SambaConfig import SambaShare
from .FolderShare import FolderShare

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw  # noqa


class SharedFolders(Gtk.Box):
    def __init__(self, shares: list[SambaShare]):
        super().__init__()

        viewport = Gtk.Viewport.new()
        clamp = Adw.Clamp.new()
        list_widget = Gtk.Box(
            spacing=45,
            orientation=Gtk.Orientation.VERTICAL
        )

        for share in shares:
            list_widget.append(FolderShare(share))

        clamp.set_child(list_widget)
        viewport.set_child(clamp)

        self.append(viewport)
