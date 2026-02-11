import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw, GObject  # noqa


class SharedFolders(Gtk.Box):
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    def __init__(self, manager=SambaConfig):
        super().__init__()

        self.manager = manager
        self.folder_shares: list[FolderShare] = []

        viewport = Gtk.Viewport.new()
        clamp = Adw.Clamp.new()

        container = Gtk.Box(
            spacing=30,
            orientation=Gtk.Orientation.VERTICAL
        )

        self.list_widget = Gtk.FlowBox(
            max_children_per_line=1,
            selection_mode=Gtk.SelectionMode.NONE,
            row_spacing=20,
        )

        btns_row = Gtk.Box(
            css_classes=['folder-share'],
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
        )

        add_btn = Gtk.Button(
            css_classes=['flat'],
            child=Adw.ButtonContent(
                icon_name='sb-plus',
                label=_('Add')
            )
        )
        
        save_btn = Gtk.Button(
            css_classes=['suggested-action'],
            child=Adw.ButtonContent(
                icon_name='sb-checkmark',
                label=_('Save')
            )
        )

        btns_row_container = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.END,
            spacing=10,
            hexpand=True,
        )

        add_btn.connect('clicked', self.on_add_btn_clicked)
        save_btn.connect('clicked', lambda w: self.emit('save', w))
        [btns_row_container.append(w) for w in [
            add_btn,
            save_btn
        ]]
        
        btns_row.append(btns_row_container)
        container.append(btns_row)
        container.append(self.list_widget)

        self.reload_shares()

        clamp.set_child(container)
        viewport.set_child(clamp)

        self.append(viewport)

    def reload_shares(self):
        shares = self.manager.list_shares()

        self.list_widget.remove_all()

        for share in shares:
            folder_share = FolderShare(share)
            self.list_widget.prepend(folder_share)
            self.folder_shares.insert(0, folder_share)

            folder_share.connect('save', lambda *args: self.reload_shares())
            folder_share.connect('delete', self.on_share_deleted)

    def on_save_btn_clicked(self, widget: Gtk.Button):
        self.manager.save()

    def on_share_deleted(self, obj, share: SambaShare):
        self.manager.delete_share(share)

        for folder_share in self.folder_shares:
            if folder_share.share.name == share.name:
                self.list_widget.remove(folder_share)
                break

    def on_add_share_save(self, obj, share: SambaShare):
        self.manager.create_share(share)
        self.reload_shares()

    def on_add_btn_clicked(self, widget: Gtk.Button):
        top_level = Gtk.Window.get_toplevels()[0]
        share = SambaShare.create_empty()

        edit_modal = EditShareDialog(top_level, share, new_share=True)
        edit_modal.connect('save', self.on_add_share_save)

        top_level.set_modal(edit_modal)
        edit_modal.show()