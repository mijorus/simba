import os
import textwrap
import shlex
from string import Template
from gi.repository import GLib

from . import terminal

class ShellScript():
    def __init__(self, path: str | None=None, content: str='', filename=None, **kwargs):
        if filename:
            path = os.path.join(GLib.get_tmp_dir(), filename)

        self.path = path

        content = textwrap.dedent(content)
        t = Template(content)
        
        for k in kwargs:
            kwargs[k] = shlex.quote(kwargs[k])

        r = t.substitute(**kwargs)

        with open(self.path, 'w+') as f:
            f.write(r)

    def host_execute(self, delete_after=True):
        p = shlex.quote(self.path)
        terminal.host_sh(['bash', '-c', f'chmod +x {p} && bash {p}'])

    def root_host_execute(self, delete_after=True):
        p = shlex.quote(self.path)
        terminal.host_sh(['pkexec', 'bash', '-c', f'chmod +x {p} && bash {p}'])

    def delete(self):
        if self.path and os.path.exists(self.path):
            os.remove(self.path)
            self.path = None