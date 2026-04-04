import gi
from ..lib.SambaConfig import SambaConfig, WarningEntry

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject  # noqa


class Warnings(Gtk.Box):
    __gtype_name__ = 'Warnings'

    def __init__(self, manager: SambaConfig,**kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self.manager = manager

        clamp = Adw.Clamp(maximum_size=800, margin_top=24, margin_bottom=24,
                          margin_start=12, margin_end=12)
        self.append(clamp)
        self.warning_rows: list[Adw.ActionRow] = []
        self._warnings: list[WarningEntry] = []

        self._group = Adw.PreferencesGroup(title=_('Warnings'))
        clamp.set_child(self._group)
        
    def reload(self):
        for r in self.warning_rows:
            self._group.remove(r)

        self._warnings: list[WarningEntry] = self.manager.scan_warnings()
        for w in self._warnings:
            self.add_warning(w)

    def add_warning(self, entry: WarningEntry):
        row = Adw.ActionRow(title=entry.title)

        if entry.description:
            row.set_subtitle(entry.description)

        icon = Gtk.Image.new_from_icon_name('dialog-warning-symbolic')
        icon.add_css_class('warning')
        row.add_prefix(icon)
        row.add_css_class('warning-row')

        self.warning_rows.append(row)
        self._group.add(row)
