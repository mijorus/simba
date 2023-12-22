import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog

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
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.END
        )

        add_btn = Gtk.Button(
            css_classes=['flat'],
            child=Adw.ButtonContent(
                icon_name='plus-symbolic',
                label=_('Add')
            )
        )

        save_btn = Gtk.Button(
            css_classes=['suggested-action'],
            child=Adw.ButtonContent(
                icon_name='save-symbolic',
                label=_('Save')
            )
        )

        add_btn.connect('clicked', self.on_add_btn_clicked)
        save_btn.connect('clicked', self.on_save_btn_clicked)
        btns_row.append(add_btn)
        list_widget.append(btns_row)

        for share in shares:
            list_widget.append(FolderShare(share))

        clamp.set_child(list_widget)
        viewport.set_child(clamp)

        self.append(viewport)

    def on_save_btn_clicked(self, widget: Gtk.Button):
        self.manager.save()

    def on_add_btn_clicked(self, widget: Gtk.Button):
        top_level = Gtk.Window.get_toplevels()[0]
        share = SambaShare.create_empty()

        edit_modal = EditShareDialog(top_level, share, new_share=True)

        top_level.set_modal(edit_modal)
        edit_modal.show()