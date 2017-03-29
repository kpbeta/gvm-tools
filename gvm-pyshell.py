# -*- coding: utf-8 -*-
# $Id$
# Description:
# GVM-PyShell for communication with the GVM UNIX-Socket over SSH.
#
# Authors:
# Raphael Grewe <raphael.grewe@greenbone.net>
#
# Copyright:
# Copyright (C) 2017 Greenbone Networks GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.

import argparse
from argparse import RawTextHelpFormatter
import code
from lxml import etree
from gvm_connection import SSHConnection, TLSConnection, UnixSocketConnection

help_text = """
    gvm-pyshell 0.1.0 (C) 2017 Greenbone Networks GmbH

    This program is a command line tool to access services
    via GMP(Greenbone Management Protocol) and
    OSP(Open Scanner Protocol).
    It is possible to start a shell like the python interactive
    mode where you could type things like "tasks = gmp.get_task".

    At the moment only these commands are support in the interactive shell:

    gmp.get_version()
    gmp.authenticate([username], [password])
    gmp.get_tasks()
    gmp.get_port_lists()

    Example:
        gmp.authenticate('admin', 'admin')
        tasks = gmp.get_tasks()

        list = tasks.xpath('task')

        taskid = list[0].attrib

        load('my_commands.gmp')

    Good introduction in working with XPath is well described here:
    https://www.w3schools.com/xml/xpath_syntax.asp

    To get out of the shell enter:
        Ctrl + D on Linux  or
        Ctrl + Z on Windows

    Further Information about the GMP Protocol can you find here:
    http://docs.greenbone.net/API/OMP/omp-7.0.html
    """


class Help(object):
    """Help class to overwrite the help function from python itself.
    """

    def __repr__(self):
        # do pwd command
        return(help_text)
help = Help()

# gmp has to be global, so the load-function has the correct namespace
gmp = None
# shell = None


def main(argv):
    global gmp
    if argv.socket is not None:
        gmp = UnixSocketConnection(sockpath=argv.socket, shell_mode=True)
    elif argv.tls:
        gmp = TLSConnection(hostname=argv.hostname, port=9390,
                            shell_mode=True)
    else:
        gmp = SSHConnection(hostname=argv.hostname, port=argv.port,
                            timeout=5, ssh_user=argv.ssh_user, ssh_password='',
                            shell_mode=True)

    if argv.script is not None:
        load(argv.script[0])

    if args.interactive:
        # Try to get the scope of the script into shell
        """vars = globals().copy()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)

        if argv.script is not None:
            shell.runsource('load("{0}")'.format(argv.script))
        shell.raw_input()
        shell.interact(banner='GVM Interactive Console. Type "help" to get\
         informationen about functionality.')
        """
        # Start the interactive Shell
        code.interact(
            banner='GVM Interactive Console. Type "help" to get informationen \
about functionality.',
            local=dict(globals(), **locals()))

    gmp.close()


def pretty(xml):
    """Prints beautiful XML-Code

    This function gets an object of list<lxml.etree._Element>
    or directly a lxml element.
    Print it with good readable format.

    Arguments:
        xml {obj} -- list<lxml.etree._Element> or directly a lxml element
    """
    if type(xml) is list:
        for item in xml:
            if etree.iselement(item):
                print(etree.tostring(item, pretty_print=True).decode('utf-8'))
            else:
                print(item)
    elif etree.iselement(xml):
        print(etree.tostring(xml, pretty_print=True).decode('utf-8'))


def load(path):
    """Loads a file into the interactive console

    Loads a file into the interactive console and execute it.
    TODO: Needs some security checks.

    Arguments:
        path {str} -- Path of file
    """
    try:
        file = open(path, 'r', newline='').read()
        exec(file, dict(globals(), **locals()))
        globals().update(locals())
    except Exception as e:
        print(str(e))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='gvm-pyshell',
        description=help_text,
        formatter_class=RawTextHelpFormatter,
        add_help=False,
        usage='gvm-pyshell [--help] [--hostname HOSTNAME] [--port PORT] \
[--xml XML] [--interactive]')

    parser.add_argument(
        '-h', '--help', action='help',
        help='Show this help message and exit.')
    parser.add_argument(
        '--hostname', default='127.0.0.1',
        help='SSH hostname or IP-Address. Default: 127.0.0.1.')
    parser.add_argument('--port', default=22, help='SSH port. Default: 22.')
    parser.add_argument(
        '--ssh-user', default='gmp',
        help='SSH Username. Default: gmp.')
    parser.add_argument(
        '--gmp-username', default='admin',
        help='GMP username. Default: admin')
    parser.add_argument(
        '--gmp-password', nargs='?', const='admin',
        help='GMP password. Default: admin.')
    parser.add_argument(
        '-i', '--interactive', action='store_true', default=False,
        help='Start an interactive Python shell.')
    parser.add_argument(
        '--tls', action='store_true',
        help='Use TLS secured connection for omp service.')
    parser.add_argument(
        'script', nargs='*',
        help='Preload gmp script. Example: myscript.gmp.')
    parser.add_argument(
        '--socket', nargs='?', const='/usr/local/var/run/openvasmd.sock',
        help='UNIX-Socket path. Default: /usr/local/var/run/openvasmd.sock.')
    args = parser.parse_args()

    main(args)