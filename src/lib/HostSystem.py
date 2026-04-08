import logging
import os
import traceback
from shlex import quote
from dataclasses import dataclass

from gi.repository import GLib
from . import terminal
from .utils import mapped_path
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
    groups: list[str]
    has_sambashare_group: bool
    is_deletable: bool=False

@dataclass(frozen=True)
class NetworkName:
    name: str
    uuid: str
    _type: str

class HostSystem():
    SAMBA_GROUP = 'sambashare'
    MANAGE_USER_PREFIX = 'samba user'

    @staticmethod
    def list_users() -> list[UserAccount]:
        data = terminal.host_sh(['cat', '/etc/passwd'])
        groups_data = terminal.host_sh(['cat', '/etc/group'])
        logindefs_max_uid = terminal.host_sh(['grep', '^SYS_UID_MAX', '/etc/login.defs'])
        logindefs_max_uid_val = 499

        if logindefs_max_uid:
            logindefs_max_uid = logindefs_max_uid.replace('SYS_UID_MAX', '').strip()
            logindefs_max_uid_val = int(logindefs_max_uid)

        output = []

        user_to_groups: dict[str, list[str]] = {}
        for grow in groups_data.split('\n'):
            grow = grow.strip()
            if (not grow) or grow.startswith('#'):
                continue
            gparts = grow.split(':')
            if len(gparts) < 4:
                continue

            gname, _, ggid, members = gparts[0], gparts[1], gparts[2], gparts[3]
            for member in members.split(','):
                member = member.strip()

                if member:
                    if not member in user_to_groups:
                        user_to_groups[member] = []

                    user_to_groups[member].append(gname)

        for row in data.split('\n'):
            row = row.strip()

            if (not row) or row.startswith('#'):
                continue

            parts = row.split(':')
            uid = int(parts[2])
            is_nologin = 'nologin' in parts[6]
            is_system_user = uid < logindefs_max_uid_val
            u_groups = user_to_groups.get(parts[0], [])

            user_data = UserAccount(
                username=  parts[0],
                password=  parts[1],
                uid=       parts[2],
                gid=       parts[3],
                comment=   parts[4], # User information/Full Name
                home=      parts[5],
                shell=     parts[6],
                is_system_user=is_system_user,
                is_nologin=is_nologin,
                groups=u_groups,
                has_sambashare_group=(HostSystem.SAMBA_GROUP in u_groups),
                is_deletable=(is_nologin and is_system_user and (HostSystem.SAMBA_GROUP in u_groups))
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

        nologin = terminal.host_sh(['which', 'nologin'])

        comment = HostSystem.MANAGE_USER_PREFIX
        pass_str = f'{pwd}\\n{pwd}\\n'

        ShellScript(
            filename='create_samba_user.sh',
            content="""
                set -e
                groupadd --force $group
                useradd --system --no-create-home --shell=$nologin $username --comment=$comment --groups=$group
                echo -ne $pwd | pdbedit --create --password-from-stdin $username
            """,
            nologin=nologin,
            username=username,
            comment=comment,
            pwd=pass_str,
            group=HostSystem.SAMBA_GROUP
        ).root_host_execute(delete_after=False)

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
    def delete_system_and_samba_user(user: UserAccount):
        users = HostSystem.list_users()
        found = False

        for u in users:
            if u.username == user.username and u.is_deletable:
                found = True
                break

        if not found:
            raise Exception(f'Missing user or not editable user: {user.username}')

        folder_exists = True

        try:
            os.listdir(mapped_path(user.home))
        except FileNotFoundError as e:
            folder_exists = False

        if folder_exists:
            raise Exception(f'Cannot delete {user.username}: home folder exists')

        ShellScript(filename="delete_samba_user.sh",
            content="""
            set -e
            pdbedit --delete $user
            userdel $user
        """, user=user.username).root_host_execute()

    @staticmethod
    def has_network_manager():
        try:
            terminal.host_sh(['which', 'nmcli'])
        except Exception as e:
            return False
        
        return True
    
    @staticmethod
    def list_printers() -> list[str]:
        printers = []

        try:
            terminal.host_sh(['which', 'lpstat'])
            output = terminal.host_sh(['lpstat', '-e'])
            printers = output.split('\n')
        except Exception as e:
            pass

        return printers

    @staticmethod
    def list_saved_networks() -> list[NetworkName]:
        result = terminal.host_sh(['nmcli', '--get-values=UUID,NAME,TYPE', '--colors=no', 'connection', 'show'])
        items = []

        for r in result.split('\n'):
            uuid, name, _type = r.split(':')
            if _type == 'loopback':
                continue

            n = NetworkName(name=name, uuid=uuid, _type=_type)
            items.append(n)

        return items
