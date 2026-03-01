import os
import gi

from ..lib.SambaConfig import SambaShare, SambaConfig
from .FolderShare import FolderShare
from .EditShareDialog import EditShareDialog

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw, GObject  # noqa


@Gtk.Template(resource_path='/it/mijorus/simba/ui/sharedfolders.ui')
class SharedFolders(Gtk.Box):
    __gtype_name__ = 'SharedFolders'
    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    add_button = Gtk.Template.Child()
    list_widget = Gtk.Template.Child()
    save_button = Gtk.Template.Child()

    def __init__(self, manager: SambaConfig):
        super().__init__()

        self.manager = manager
        self.folder_shares: list[FolderShare] = []
        self.add_button.connect('clicked', self.on_add_btn_clicked)
        self.save_button.connect('clicked', lambda w: self.emit('save', w))

    def reload_shares(self):
        if not self.manager.is_config_supported():
            return

        shares = self.manager.list_shares()
        shares.reverse()

        for i, w in enumerate(self.folder_shares):
            self.list_widget.remove(w)

        self.folder_shares = []

        for share in shares:
            folder_share = FolderShare(share)
            self.list_widget.add(folder_share)
            self.folder_shares.append(folder_share)

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