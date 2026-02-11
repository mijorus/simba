import os
import gi

from ..lib.SambaConfig import SambaShare
from .EditShareDialog import EditShareDialog

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw, GObject  # noqa


class FolderShare(Adw.PreferencesGroup):
    FEATURE_ICON_PIXEL_SIZE = 30

    __gsignals__ = {
        "save": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
        "delete": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object, )),
    }

    def __init__(self, share: SambaShare):
        super().__init__(
            title=share.name,
            description=share.comment,
            css_classes=["folder-share"],
        )

        self.share = share

        header_suffix_container = Gtk.Box(
            valign=Gtk.Align.CENTER,
            orientation=Gtk.Orientation.HORIZONTAL,
            css_classes=['linked'],
        )

        edit_button = Gtk.Button(
            child=Adw.ButtonContent(
                icon_name='pencil-symbolic',
                label=_('Edit')
            )
        )

        edit_button.connect('clicked', self.on_edit_btn_clicked)

        delete_button = Gtk.Button(
            child=Adw.ButtonContent(
                icon_name='user-trash-symbolic',
                css_classes=['error'],
                label=_('Remove')
            )
        )

        delete_button.connect('clicked', self.on_delete_btn_clicked)

        [header_suffix_container.append(w) for w in [
            edit_button,
            delete_button
        ]]

        features_list = Gtk.ListBox(css_classes=['boxed-list'])

        path_row = Adw.ActionRow(title=_('Path'), subtitle=share.share_path)
        path_row.add_prefix(
            Gtk.Image(icon_name='file-cabinet-symbolic', pixel_size=self.FEATURE_ICON_PIXEL_SIZE)
        )

        read_only_row = False
        if not share.writeable:
            read_only_row = Adw.ActionRow(title=_('Read only'), subtitle=_("The content of this share can't be modified"))
            read_only_row.add_prefix(
                Gtk.Image(icon_name='eye-symbolic', pixel_size=self.FEATURE_ICON_PIXEL_SIZE)
            )

        [features_list.append(w) if w else None for w in [
            path_row,
            read_only_row
        ]]

        self.set_header_suffix(header_suffix_container)
        self.add(features_list)

    def on_edit_btn_clicked(self, widget: Gtk.Button):
        top_level = Gtk.Window.get_toplevels()[0]
        edit_modal = EditShareDialog(top_level, self.share)

        edit_modal.connect('save', self.on_edit_share_save)

        top_level.set_modal(edit_modal)
        edit_modal.show()

    def on_delete_btn_clicked(self, widget: Gtk.Button):
        self.emit('delete', self.share)

    def on_edit_share_save(self, widget, share: SambaShare):
        self.emit('save', share)