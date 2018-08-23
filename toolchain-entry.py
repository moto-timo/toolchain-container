#!/usr/bin/env python

# toolchain-entry.py
#
# This script is to present arguments to the user of the container and then
# chuck them over to the scripts that actually do the work.
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
import subprocess
import tempfile
import shutil
import stat
import traceback

def download_sdk(url, dest):
    cmd = "curl -# -o {} {}".format(dest, url).split()

    try:
        print "Attempting to download {}".format(url)
        subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError:
        errormsg = 'Unable to download "{}".'.format(args.url)
        raise Exception(errormsg)


def setup_sdk(installer, dest):
    cmd = "{} -d {} -y".format(installer, dest).split()
    try:
        subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError:
        errormsg = 'Unable to setup sdk.'.format(args.url)
        raise Exception(errormsg)


parser = argparse.ArgumentParser(epilog="NOTE: The --toolchain is the path as "
                                        "seen inside of the container. So if "
                                        "-v /foo:/bar was passed to docker, "
                                        "--toolchain should be set to /bar.")

parser.add_argument('--workdir', default='/workdir',
                    help='The active directory once the container is running. '
                         'In the abscence of the "id" argument, the uid and '
                         'gid of the workdir will also be used for the user '
                         'in the container.')

parser.add_argument("--id",
                    help='uid and gid to use for the user inside the '
                         'container. It should be in the form uid:gid')

parser.add_argument("--cmd",default='',
                    help='command to run after setting up container. '
                         'Often used for testing.')

parser.add_argument("--url", help="url of the sdk installer")

parser.add_argument("--toolchain", default='/sdk',
                    help="Directory containing the prepared sdk. "
                         "Or the location to prepare the sdk if url is "
                         "specfied.")

args = parser.parse_args()

try:
    #if not os.path.exists(args.workdir):
    #    os.mkdir(args.workdir)

    setupscript = glob.glob(os.path.join(args.toolchain, "environment-setup-*"))
    toolchainfound = setupscript and os.path.exists(os.path.join(args.toolchain, "sysroots"))

    if toolchainfound and args.url:
        errormsg = ('SDK or build tree toolchain was found in {} yet "--url" was also '
                    'specified. Cowardly refusing to overwrite existing toolchain.')
        errormsg = errormsg.format(args.toolchain)
        raise Exception(errormsg)

    elif not toolchainfound and not args.url:
        errormsg = ('SDK or build tree toolchain was not found in {}. Install it using "--url" or '
                    'bind mount it to {}')
        errormsg = errormsg.format(args.toolchain, args.toolchain)
        raise Exception(errormsg)

    if args.url:
        # Add a special mechanism for installing directly from the file
        # rather than trying to download. For example let's say a user had
        # already downloaded a large sdk installer to the workdir. Even
        # copying the file using curl with FILE: might take a while and will
        # also use more space.
        #
        # So if the "url" starts with "/" then treat it as something that
        # should directly be installed.
        if args.url.startswith('/'):
            sdk_installer = args.url
        else:
            tempdir = tempfile.mkdtemp(prefix="sdk-download",
                                       dir=args.toolchain)
            sdk_installer = os.path.join(tempdir, "sdk-installer.sh")
            download_sdk(args.url, sdk_installer)

        oldmode = os.stat(sdk_installer).st_mode
        os.chmod(sdk_installer, stat.S_IXUSR | oldmode)

        setup_sdk(sdk_installer, args.toolchain)
        setupscript = glob.glob(os.path.join(args.toolchain,
                                "environment-setup-*"))

        # Since we don't want the user to have to download a very large image
        # again if the install fails, we don't delete the tmpdir on failure.
        try:
            shutil.rmtree(tempdir, ignore_errors=True)
        except NameError:
            pass

    # Source the environment setup script and run bash
    #cmd = 'bash -c'.split()
    #args = 'cd {}; . {}; exec bash -i'.format(args.workdir, setupscript[0])

    # continue here

    idargs = ""
    if args.id:
        uid, gid = args.id.split(":")
        idargs = "--uid={} --gid={}".format(uid, gid)

    elif args.workdir == '/home/sdkuser':
        # If the workdir wasn't specified pick a default uid and gid since
        # usersetup won't be able to calculate it from the non-existent workdir
        idargs = "--uid=1000 --gid=1000"


    if args.url:
        urlarg = "--url={}".format(args.url)
    else:
        urlarg = ""

    cmd = """usersetup.py --username=sdkuser --workdir={workdir} {idargs} toolchain-launch.py """\
          """--workdir={workdir} --toolchain={toolchain} {cmdarg}"""
    cmd = cmd.format(workdir=args.workdir, idargs=idargs, toolchain=args.toolchain, cmdarg=args.cmd).split()
    os.execvp(cmd[0], cmd)

except Exception as e:
    traceback.print_exc()
    sys.exit(1)

