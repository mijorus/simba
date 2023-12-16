import gi
from ..lib.custom_tags import set_custom_tags, get_custom_tags
from ..lib.localized_tags import get_localized_tags, get_countries_list
from .CustomPopover import CustomPopover

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, GLib, Adw  # noqa


class CustomTagEntry(CustomPopover):
    def __init__(self, flowbox_child: Gtk.FlowBoxChild, parent: Gtk.Window):
        super().__init__(parent=parent)

        self.emoji_button = flowbox_child.get_child()
        self.flowbox_child = flowbox_child

        popover_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, name='custom_tag_entry')
        self.relative_widget_hexcode = self.emoji_button.emoji_data['hexcode']

        max_tags_lengh = 30
        
        from ..assets.emoji_list import emojis
        default_tags = emojis[self.relative_widget_hexcode]['tags']

        localized_tags = []

        settings: Gio.Settings = Gio.Settings.new('it.mijorus.smile')
        if settings.get_boolean('use-localized-tags'):
            tl = get_localized_tags(settings.get_string('tags-locale'), self.relative_widget_hexcode, Gio.Application.get_default().datadir)
            localized_tags = ', '.join(tl)

        if len(default_tags) > max_tags_lengh:
            default_tags = default_tags[0:max_tags_lengh] + '...'

        if len(localized_tags) > max_tags_lengh:
            localized_tags = localized_tags[0:max_tags_lengh] + '...'

        popover_content.append(
            Gtk.Label(
                label=_('<b>{emoji} Edit custom tags</b>').format(emoji=self.emoji_button.emoji_data["emoji"]),
                use_markup=True,
                margin_bottom=10,
                css_classes=['heading']
            )
        )

        self.entry = Gtk.Entry(
            text=get_custom_tags(self.emoji_button.hexcode),
            placeholder_text=_("List of custom tags, separated  by comma")
        )

        popover_content.append(self.entry)
        self.entry.connect('activate', self.handle_activate)

        label_text = _("<small><b>Default tags</b>: {default_tags}</small>").format(default_tags=default_tags)
        if len(localized_tags) > 0:
            label_text += f"\n<small><b>{get_countries_list()[settings.get_string('tags-locale')]['language']} tags</b>: {localized_tags}</small>"

        
        label = Gtk.Label(label=label_text, use_markup=True, margin_top=10)
        popover_content.append(label)
        popover_content.append(
            Gtk.Label(label=_("<small>Press Enter to save or ESC to dismiss</small>"), use_markup=True, margin_top=10, css_classes=['dim-label'])
        )

        # self.flowbox_child.set_as_selected()

        self.set_content(popover_content)

    def handle_activate(self, user_data):
        set_custom_tags(self.relative_widget_hexcode, self.entry.get_text())
        self.request_close()
        return True