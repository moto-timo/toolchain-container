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

parser = argparse.ArgumentParser(epilog="NOTE: The --toolchain is the path as "
                                        "seen inside of the container. So if "
                                        "-v /foo:/bar was passed to docker, "
                                        "--toolchain should be set to /bar.")

parser.add_argument('--workdir', default='/home/pokyuser',                                                                                                                                                  
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

parser.add_argument("--toolchain", default='/toolchain',
                    help="Directory containing the prepared sdk. "
                         "Or the location to prepare the sdk if url is "
                         "specfied.")

args = parser.parse_args()

idargs = ""                                                                                                                                                                                                 
if args.id:                                                                                                                                                                                                 
    uid, gid = args.id.split(":")                                                                                                                                                                           
    idargs = "--uid={} --gid={}".format(uid, gid)                                                                                                                                                           
                                                                                                                                                                                                            
elif args.workdir == '/home/pokyuser':                                                                                                                                                                      
    # If the workdir wasn't specified pick a default uid and gid since                                                                                                                                      
    # usersetup won't be able to calculate it from the non-existent workdir                                                                                                                                 
    idargs = "--uid=1000 --gid=1000"


if args.url:
    urlarg = "--url={}".format(args.url)
else:
    urlarg = ""

cmd = """usersetup.py --username=sdkuser --workdir={workdir} {idargs} toolchain-launch.py {urlarg} """\
      """--toolchain={toolchain}"""
cmd = cmd.format(workdir=args.workdir, idargs=idargs, urlarg=urlarg, toolchain=args.toolchain).split()
os.execvp(cmd[0], cmd)
