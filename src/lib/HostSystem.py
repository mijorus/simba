import logging
from shlex import quote

from . import terminal

class HostSystem():
    MANAGE_USER_PREFIX = 'samba user - '

    @staticmethod
    def list_users():
        data = terminal.host_sh(['cat', '/etc/passwd'])
        output = []

        for row in data.split('\n'):
            row = row.strip()

            if (not row) or row.startswith('#'):
                continue

            parts = row.split(':')
            user_data = {
                'username':  parts[0],
                'password':  parts[1],
                'uid':       parts[2],
                'gid':       parts[3],
                'comment':   parts[4], # User information/Full Name
                'home':      parts[5],
                'shell':     parts[6]
            }

            output.append(user_data)

        return output
    
    @staticmethod
    def create_system_user(username: str, comment:str):
        exists = False
        users = HostSystem.list_users()

        for u in users:
            if u['username'] == username:
                exists = True
                break

        if exists:
            raise Exception(f'User {username} already exists')

        comment = HostSystem.MANAGE_USER_PREFIX + comment

        nologin = terminal.host_sh(['which', 'nologin'])
        terminal.host_sh(['pkexec', 'bash', '-c', 'useradd', '--system', '--no-create-home',
                          f'--shell={quote(nologin)}', username, f'--comment={quote(comment)}'])
        
    @staticmethod
    def delete_system_user(uid: str):
        nologin = terminal.host_sh(['which', 'nologin'])
        users = HostSystem.list_users()
        user = None

        for u in users:
            if u['uid'] == uid and u['shell'] == nologin and \
                u['comment'].startswith(HostSystem.MANAGE_USER_PREFIX):
                user = u
                break

        if user:
            terminal.host_sh(['pkexec', 'bash', '-c', 'userdel', user['username']])
        else:
            logging.warning(f"Can't delete user {uid}: user is either missing or was not created by this app")