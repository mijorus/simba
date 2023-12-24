import sys
import gi
import logging
import os

from .lib.constants import *
from .utils import make_option
from .MainWindow import MainWindow

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Gdk, Adw, GLib  # noqa


LOG_FILE_MAX_N_LINES = 5000
LOG_FOLDER = GLib.get_user_cache_dir() + '/logs'


class Simba(Adw.Application):
    def __init__(self, **kwargs) -> None:
        self.application_id = APP_ID
        super().__init__(application_id=self.application_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

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
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/it/mijorus/simba/assets/style.css')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
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
            application_name='simba',
            application_icon='it.mijorus.simba',
            developer_name='Lorenzo Paderi',
            website='https://simba.mijorus.it',
            issue_url='https://github.com/mijorus/simba',
            debug_info='Type the answer to life, the universe, and everything',
            copyright='(C) 2022 Lorenzo Paderi\n\nLocalized tags by milesj/emojibase, licensed under the MIT License',
        )

        self.about.set_transient_for(self.props.active_window)
        self.about.present()

def main(version: str, datadir: str) -> None:
    log_file = f'{LOG_FOLDER}/{APP_NAME}.log'

    if not os.path.exists(LOG_FOLDER):
         os.makedirs(LOG_FOLDER)

    print('Logging to file ' + log_file)

    # Clear log file if it's too big
    log_file_size = 0
    if os.path.exists(log_file): 
        with open(log_file, 'r') as f:
            log_file_size = len(f.readlines())
        
        if log_file_size > LOG_FILE_MAX_N_LINES:
            with open(log_file, 'w+') as f:
                f.write('')


    logging.basicConfig(
        filename=log_file,
        filemode='a',
        encoding='utf-8',
        level= logging.DEBUG,
        force=True
    )

    app = Simba(version=version, datadir=datadir)
    app.run(sys.argv)
