import os
import gi

from ..lib.SambaConfig import SambaShare
from .EditShareDialog import EditShareDialog

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw  # noqa


class FolderShare(Adw.PreferencesGroup):
    FEATURE_ICON_PIXEL_SIZE = 30

    def __init__(self, share: SambaShare):
        print(share.writeable, share.name)
        detail = '' if share.writeable else _('[Read only]')

        super().__init__(
            title=(share.name + ' ' +detail),
            description=share.comment,
            css_classes=["folder-share"],
        )

        self.share = share

        self.edit_button = Gtk.Button(
            css_classes=['flat'],
            child=Adw.ButtonContent(
                icon_name='pencil-symbolic',
                label=_('Edit')
            )
        )

        self.edit_button.connect('clicked', self.on_edit_btn_clicked)

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

        self.set_header_suffix(self.edit_button)
        self.add(features_list)

    def on_edit_btn_clicked(self, widget: Gtk.Button):
        top_level = Gtk.Window.get_toplevels()[0]
        edit_modal = EditShareDialog(top_level, self.share)

        top_level.set_modal(edit_modal)
        edit_modal.show()