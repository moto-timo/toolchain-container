#!/usr/bin/env python

# toolchain-launch.py
#
# Copyright (C) 2016 Intel Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import argparse
import os
import sys
import glob
import traceback


parser = argparse.ArgumentParser()

parser.add_argument("--workdir", default='/workdir',
                    help="Directory containing the prepared extensible sdk. "
                         "Or the location to prepare the sdk if url is "
                         "specfied.")
parser.add_argument("--toolchain", default='/toolchain',
                    help="Directory containing the prepared sdk. "
                         "Or the location to prepare the sdk if url is "
                         "specfied.")

parser.add_argument("cmd", metavar="CMD", nargs="*");

args = parser.parse_args()

try:
    if not os.path.exists(args.workdir):
        os.mkdir(args.workdir)

    setupscript = glob.glob(os.path.join(args.toolchain, "environment-setup-*"))

    # Source the environment setup script and run bash
    cmd = 'bash -c'.split()
    if args.cmd:
        args = 'cd {workdir}; . {setupscript}; exec bash -c "{cmd}"'.format(workdir=args.workdir, setupscript=setupscript[0], cmd=" ".join(args.cmd))
    else:
        args = 'cd {workdir}; . {setupscript}; exec bash -i'.format(workdir=args.workdir, setupscript=setupscript[0])

    os.execvp(cmd[0], cmd + [args])

except Exception as e:
    traceback.print_exc()
    sys.exit(1)
