import logging
import os
import traceback
from shlex import quote
from dataclasses import dataclass

from gi.repository import GLib
from . import terminal
from .ShellScript import ShellScript


@dataclass(frozen=True)
class UserAccount:
    """Represents a system user account entry."""
    username: str
    password: str
    uid: str
    gid: str
    comment: str
    home: str
    shell: str
    is_system_user: bool
    is_nologin: bool

class HostSystem():
    MANAGE_USER_PREFIX = 'samba user - '

    @staticmethod
    def list_users() -> list[UserAccount]:
        data = terminal.host_sh(['cat', '/etc/passwd'])
        logindefs_max_uid = terminal.host_sh(['grep', '^SYS_UID_MAX', '/etc/login.defs'])
        logindefs_max_uid_val = 499

        if logindefs_max_uid:
            logindefs_max_uid = logindefs_max_uid.replace('SYS_UID_MAX', '').strip()
            logindefs_max_uid_val = int(logindefs_max_uid)

        output = []

        for row in data.split('\n'):
            row = row.strip()

            if (not row) or row.startswith('#'):
                continue

            parts = row.split(':')
            uid = int(parts[2])

            user_data = UserAccount(
                username=  parts[0],
                password=  parts[1],
                uid=       parts[2],
                gid=       parts[3],
                comment=   parts[4], # User information/Full Name
                home=      parts[5],
                shell=     parts[6],
                is_system_user= uid < logindefs_max_uid_val,
                is_nologin= 'nologin' in parts[6],
            )

            output.append(user_data)

        return output
    
    @staticmethod
    def create_system_and_samba_user(username: str, comment: str, pwd: str):
        exists = False
        users = HostSystem.list_users()

        for u in users:
            if u.username == username:
                exists = True
                break

        if exists:
            raise Exception(f'User {username} already exists')

        comment = HostSystem.MANAGE_USER_PREFIX + comment

        nologin = terminal.host_sh(['which', 'nologin'])

        ShellScript(
            filename='create_samba_user.sh',
            content="""
                set -e
                useradd --system --no-create-home --shell=$nologin $username $comment
                echo -ne "$pwd" | pdbedit --create --password-from-stdin $username
            """,
            nologin=nologin,
            username=username,
            comment=comment,
            pwd=pwd
        ).root_host_execute(delete_after=True)

        users = HostSystem.list_users()
        for u in users:
            if u.username == username:
                return u
            
        return None
    
    @staticmethod
    def get_user(username: str):
        users = HostSystem.list_users()

        for u in users:
            if u.username == username:
                return u
            
        return None
        
    @staticmethod
    def delete_system_user(uid: str):
        nologin = terminal.host_sh(['which', 'nologin'])
        users = HostSystem.list_users()
        user = None

        for u in users:
            if u.uid == uid and u.is_nologin and \
                u.comment.startswith(HostSystem.MANAGE_USER_PREFIX):
                user = u
                break

        if user:
            terminal.host_sh(['pkexec', 'bash', '-c', 'userdel', user.username])
        else:
            logging.warning(f"Can't delete user {uid}: user is either missing or was not created by this app")