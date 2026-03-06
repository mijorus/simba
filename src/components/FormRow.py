import re
import os
import gi
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject  # noqa



class FormRow(Gtk.Box):
    def __init__(self, name: str, title: str, text: str, max_length=100, description: str='', valitator: callable=None, after_validation: callable=None) -> None:
        """
            validator: The validator function should return False if the string is not valid
        """
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            margin_bottom=10
        )

        self._is_valid = True
        if valitator:
            self._is_valid = False

        self.max_length = max_length
        self.name = name

        container = Gtk.ListBox()

        self.entry = Adw.EntryRow(
            title=title,
            text=text,
            enable_emoji_completion=False
        )

        self.entry.get_delegate().set_max_length(max_length)

        self.validator = valitator
        self.after_validation = after_validation
        self.entry.connect('changed', self.on_entry_changed)

        desc = Gtk.Label(
            label=description + ' (max. {max_char} characters)'.format(max_char=max_length),
            halign=Gtk.Align.START,
            css_classes=['dim-label', 'toolbar', 'caption']
        )

        container.append(self.entry)

        self.append(container)
        self.append(desc)

    
    def on_entry_changed(self, widget):
        if self.validator:
            self._is_valid = self.validator(self.name, widget.get_text())

            if not self._is_valid:
                widget.add_css_class('error')
            else:
                widget.remove_css_class('error')

            if self.after_validation:
                self.after_validation()
