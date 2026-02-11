import os
import textwrap
import shlex
from string import Template

from . import terminal

class ShellScript():
    def __init__(self, path, content, **kwargs):
        self.path = path
        content = textwrap.dedent(content)
        t = Template(content)
        
        for k in kwargs:
            kwargs[k] = shlex.quote(kwargs[k])

        r = t.substitute(**kwargs)

        with open(path, 'w+') as f:
            f.write(r)

    def host_execute(self):
        if self.path:
            terminal.host_sh(['bash', '-c', self.path])
        else:
            raise Exception('File has been removed')

    def root_host_execute(self):
        if self.path:
            terminal.host_sh(['pkexec', 'bash', '-c', self.path])
        else:
            raise Exception('File has been removed')

    def delete(self):
        if self.path and os.path.exists(self.path):
            os.remove(self.path)
            self.path = None