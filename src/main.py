import sys
import gi

from .utils import make_option
from .MainWindow import MainWindow
from .ShortcutsWindow import ShortcutsWindow
from .components.UpdateDialog import UpdateDialog
from .lib.DbusService import DbusService, GNOME_EXTENSION_LINK

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, Adw, GLib  # noqa


class Simba(Adw.Application):
    def __init__(self, **kwargs) -> None:
        self.application_id = "it.mijorus.simba"
        super().__init__(application_id=self.application_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

        entries = [
            make_option('start-hidden'),
            make_option('version')
        ]

        self.add_main_option_entries(entries)

        self.datadir = kwargs['datadir']
        self.version = kwargs['version']
        self.about = None
        self.window = None

    def do_handle_local_options(self, options):
        if options.contains('version'):
            print(self.version)
            return 0

        return -1

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(application=self)

            # self.create_action("preferences", lambda w, e: self.on_preferences_action())
            self.create_action("about", self.on_about_action)

        else:
            self.window.set_visible(True)
            self.window.on_activation()

        self.window.present()

    # def on_preferences_action(self):
    #     pref_window = Settings(self.application_id, transient_for=self.window)
    #     pref_window.present()

    def create_action(self, name, callback):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def on_about_action(self, widget, event):
        self.about = Adw.AboutWindow(
            version=self.version,
            comments='An emoji picker',
            application_name='Smile',
            application_icon='it.mijorus.smile',
            developer_name='Lorenzo Paderi',
            website='https://smile.mijorus.it',
            issue_url='https://github.com/mijorus/smile',
            debug_info='Type the answer to life, the universe, and everything',
            copyright='(C) 2022 Lorenzo Paderi\n\nLocalized tags by milesj/emojibase, licensed under the MIT License',
        )

        self.about.set_transient_for(self.props.active_window)
        self.about.present()

def main(version: str, datadir: str) -> None:
    app = Simba(version=version, datadir=datadir)

    app.run(sys.argv)
