# Copyright (C) 2015-2016 Intel Corporation
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
import pytest
import re
import shlex
import subprocess
import time
import uuid
import os

def remove_container(name):
    cmd = shlex.split("docker rm -f {}".format(name))

    subprocess.run(cmd, check=True, stdout=subprocess.PIPE)

def run_container(testimage, sdkdir, workdir, name="", url=""):
    print("{}, {}, {}, {}".format(testimage, sdkdir, workdir, url))
    if url is "":
        urlarg = ""
    else:
        urlarg = "--url {}".format(url)

    if name is "":
        namearg = ""
    else:
        namearg = "--name {}".format(name)
		
    cmd = ("docker run -t  -v {sdkdir}:/sdk -v {workdir}:/workdir {namearg} "
           "{testimage} {urlarg} "
           " --workdir /workdir").format(sdkdir=sdkdir, workdir=workdir, 
                                  testimage=testimage, urlarg=urlarg,
                                   namearg=namearg)
    cmd = shlex.split(cmd)

    with open("/tmp/mylog", "w") as log:
        subprocess.Popen(cmd, stdout=log,
                         stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

    # Waiting for container to start
    with open("/tmp/mylog", "r") as log:
        found = False
        totaltime = 0

        # This basically looks for the user prompt
        while not found and totaltime < 5:
            if re.match(r'.*sdkuser@.*/workdir\$', log.readline()):
                found = True
                break
            time.sleep(.5)
            totaltime += .5
            log.seek(0)

        if not found:
            remove_container(name)
            raise Exception("prompt not found in: {}".format(log.readlines()))

# Fixture returns the name of a running container. The fixture nicely creates
# the sentinel files the launcher looks for.
@pytest.fixture
def fake_container(testimage, tmpdir):
#sdkdir = tmpdir.mkdir('sdk')
    tmpdir.mkdir('sdk').join('environment-setup-foo').write('')
    tmpdir.join('sdk').mkdir('sysroots')
    tmpdir.mkdir('workdir')
    
#    sdkdir.join('environment-setup-foo').write('')
#    sdkdir.join('sysroots').write('') 
    
    name = str(uuid.uuid4())

    run_container(testimage, str(tmpdir.join('sdk')), str(tmpdir.join('workdir')), name=name)

    yield name

    remove_container(name)

def test_dumb_init(fake_container):
    username = "root"
    expected = ("1 {} /usr/bin/dumb-init -- /usr/bin/toolchain-entry.py "
                "--workdir /workdir\n".format(username))

    cmd = ('docker exec {} bash -c "ps -w -w h -C dumb-init '
           '-o pid:1,user:{},args"').format(fake_container, len(username))
    cmd = shlex.split(cmd)

    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    assert result.stdout.decode() == expected, result.stdout.decode()
