import os
import textwrap
import shlex
from string import Template
from gi.repository import GLib

from .constants import RUN_ID, APP_ID
from . import terminal, utils

class ShellScript():
    def __init__(self, filename, content: str='', **kwargs):
        # GLib.get_user_cache_dir()
        path = os.path.join(GLib.get_user_cache_dir(), filename)
        self.path = path

        content = textwrap.dedent(content)
        t = Template(content)
        
        for k in kwargs:
            kwargs[k] = shlex.quote(kwargs[k])

        r = t.safe_substitute(**kwargs)
        # r = shlex.quote(r)

        with open(path, 'w+') as f:
            f.write(r)
        # terminal.host_sh(['bash', '-c', f'echo -n {r} > {self.path}'])

    def host_execute(self, delete_after=True, root=False):
        p = shlex.quote(self.path)
        err = None

        try:
            if root:
                terminal.host_sh(['pkexec', 'bash', '-c', f'chmod +x {p} && bash {p}'])
            else:
                terminal.host_sh(['bash', '-c', f'chmod +x {p} && bash {p}'])
        except Exception as e:
            err = e

        # if delete_after:
        #     self.delete()

        if err:
            raise err

    def root_host_execute(self, delete_after=True):
        self.host_execute(delete_after, root=True)

    def delete(self):
        terminal.host_sh(['rm', '-f', self.path])