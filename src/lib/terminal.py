import subprocess
import re
import logging
import threading
from typing import Callable, List, Union, Optional
import logging

def host_sh(command: List[str], return_stderr=False, hide_log=False, **kwargs) -> str:
    try:
        cmd = ['flatpak-spawn', '--host', *command]
        
        if hide_log:
            print(f'Running ***')
        else:
            print(f'Running {command}')

        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        output.check_returncode()
    except subprocess.CalledProcessError as e:
        print(str(e.stderr))
        if return_stderr:
            return e.stderr.decode()

        raise e

    return re.sub(r'\n$', '', output.stdout.decode() + (output.stderr.decode() if return_stderr else ''))

def sandbox_sh(command: List[str], return_stderr=False, hide_log=False, **kwargs) -> str:
    try:
        cmd = [*command]

        if hide_log:
            print(f'Running ***')
        else:
            print(f'Running {command}')

        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        output.check_returncode()
    except subprocess.CalledProcessError as e:
        if return_stderr:
            return e.stderr.decode()

        raise e

    return re.sub(r'\n$', '', output.stdout.decode() + (output.stderr.decode() if return_stderr else ''))

def host_threaded_sh(command: List[str], callback: Optional[Callable[[str], None]]=None, return_stderr=False):
    def run_command(command: List[str], callback: Optional[Callable[[str], None]]=None):
        try:
            output = host_sh(command, return_stderr)

            if callback:
                callback(re.sub(r'\n$', '', output))

        except subprocess.CalledProcessError as e:
            logging.error(e.stderr)
            raise e

    thread = threading.Thread(target=run_command, daemon=True, args=(command, callback, ))
    thread.start()