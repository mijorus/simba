import re
import os
import gi
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject  # noqa



class FormRow(Gtk.Box):
    def __init__(self, name: str, title: str, text: str, max_length=100, min_length=0, show_constrains=True,
                description: str='', validator: callable=None, after_validation: callable=None, is_passwd=False) -> None:
        """
            validator: The validator function should return False if the string is not valid
        """
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            margin_bottom=10
        )

        self._is_valid = True
        self.after_validation = None

        self.max_length = max_length
        self.min_length = min_length
        self.name = name

        container = Gtk.ListBox(css_classes=['boxed-list'])

        if is_passwd:
            self.entry = Adw.PasswordEntryRow(
                title=title,
                text=text,
                enable_emoji_completion=False
            )
        else:
            self.entry = Adw.EntryRow(
                title=title,
                text=text,
                enable_emoji_completion=False
            )

        self.entry.get_delegate().set_max_length(max_length)

        self.validator = validator

        if validator:
            self.on_entry_changed(self.entry)

        self.after_validation = after_validation
        self.entry.connect('changed', self.on_entry_changed)

        desc_suffix = ''
        if show_constrains:
            desc_suffix = _(' (max. {max_char})').format(max_char=max_length)

            if min_length:
                desc_suffix = _(' (min. {min_char}, max. {max_char})').format(max_char=max_length, min_char=min_length)

        desc_string = ' '.join([description, desc_suffix])

        container.append(self.entry)
        self.append(container)

        if desc_string.strip():
            desc = Gtk.Label(
                label=desc_string,
                halign=Gtk.Align.START,
                css_classes=['dim-label', 'toolbar', 'caption']
            )

            self.append(desc)

    def on_entry_changed(self, widget):
        if self.validator:
            text = widget.get_text()
            l = len(text)

            if (l > self.max_length) or (l < self.min_length):
                self._is_valid = False
            else:
                self._is_valid = self.validator(self.name, widget.get_text())

            if not self._is_valid:
                widget.add_css_class('error')
            else:
                widget.remove_css_class('error')

            if self.after_validation:
                self.after_validation()
