import os
import gi

from ..lib.SambaConfig import SambaShare

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Adw  # noqa


class FolderShare(Adw.PreferencesGroup):
    def __init__(self, share: SambaShare):
        super().__init__(
            title=share.name,
            description=share.comment
        )

        self.edit_button = Gtk.Button(
            css_classes=['flat'],
            icon_name='pencil-symbolic',
            label=_('Edit')
        )

        features_list = Gtk.ListBox(css_classes=['boxed-list'])

        path_icon = Gtk.Image(icon_name='file-cabinet-symbolic', pixel_size=30)
        path_row = Adw.ActionRow(
            title=_('Path'),
            subtitle=share.share_path
        )
        path_row.add_prefix(path_icon)

        [features_list.append(w) for w in [path_row]]

        self.set_header_suffix(self.edit_button)
        self.add(features_list)