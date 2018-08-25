Toolchain Container
===================

This repo provides a toolchain container which sets up cross compilation environment for either SDK or build tree toolchain by automatically loading the environment-setup-\* script.


# Running with SDK Toolchain

  * **Install SDK Toolchain**

    By default this container assumes SDK is located in `/sdk`. The SDK needs to be installed separately using the `--url` option.

    * **Linux**

      ```
      docker run --rm -it -v /home/user/sdk:/sdk <repo>/toolchain --url http://someserver/sdk_installer.sh
      ```

    * **Windows/Mac**

      ```
      docker run --rm -it -v sdkvolume:/sdk <repo>/toolchain --url http://someserver/sdk_installer.sh
      ```

    You should now see:

    ```
    Attempting to download http://someserver/sdk_installer.sh
    ######################################################################## 100.0%
    Poky (Yocto Project Reference Distro) SDK installer version 2.5+snapshot
    ========================================================================
    You are about to install the SDK to "/sdk". Proceed[Y/n]? Y
    Extracting SDK........................................................................................................done
    Setting it up...done
    SDK has been successfully set up and is ready to be used.
    Each time you wish to use the SDK in a new shell session, you need to source the environment setup script e.g.
     $ . /sdk/environment-setup-i586-poky-linux
    sdkuser@ubuntu:~$
    ```


  * **Build with SDK Toolchain**

    The following instructions assume `/workdir` is mounted with the location of source tree which needs to be compiled using SDK toolchain.

    * **Linux**

      ```
      docker run --rm -it -v /home/user/sdk:/sdk -v /home/user/workdir:/workdir <repo>/toolchain
      ```

    * **Windows/Mac**

      ```
      docker run --rm -it -v sdkvolume:/sdk -v myvolume:/workdir <repo>/toolchain
      ```


# Running with Build Tree Toolchain


  * **Prepare Build Tree Toolchain**

    Follow instructions on https://github.com/crops/poky-container to setup a crops/poky container, then follow the Yocto Project Quick Build manual (https://www.yoctoproject.org/docs/latest/brief-yoctoprojectqs/brief-yoctoprojectqs.html) to clone the poky repo and run `bitbake meta-ide-support` to prepare the build tree toolchain.

  * **Build with Build Tree Toolchain**

    The following assumes `/workdir/poky/build/tmp` (`TMPDIR` prepared by crops/poky container) has been populated with build tree toolchain. Set the `--toolchain` option to the build tree toolchain location containing `environment-setup-*` script.

    * **Linux**

      ```
      docker run --rm -it -v /home/user/workdir:/workdir <repo>/toolchain --toolchain /workdir/poky/build/tmp
      ```

    * **Windows/Mac**

      ```
      docker run --rm -it -v myvolume:/workdir <repo>/toolchain --toolchain /workdir/poky/build/tmp
      ```


# Examples

  * **CMake**

    To build a CMake project mounted on `/workdir` using SDK toolchain:

    * **Linux**

      ```
      docker run --rm -it -v /home/user/sdk:/sdk -v /home/user/workdir:/workdir <repo>/toolchain --cmd "cmake . && make"
      ```

    * **Windows/Mac**

      ```
      docker run --rm -it -v sdkvolume:/sdk <repo>/toolchain -v myvolume:/workdir <repo>/toolchain --cmd "cmake . && make"
      ```

  * **Autotools**

    To build an autotools project mounted on `/workdir` using SDK toolchain:

    * **Linux**

      ```
      docker run --rm -it -v /home/user/sdk:/sdk -v /home/user/workdir:/workdir <repo>/toolchain --cmd "./configure \$CONFIGURE_FLAGS && make"
      ```

    * **Windows/Mac**

      ```
      docker run --rm -it -v sdkvolume:/sdk <repo>/toolchain -v myvolume:/workdir <repo>/toolchain --cmd "./configure \$CONFIGURE_FLAGS && make"
      ```
