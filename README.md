# CFModpackImporter

Download mods for curseforge modpacks and create a zip of files to be added to a modded instance in various third party launchers.


## Building and Running

First, make sure python3 is installed. On windows, the executable name may be `python` not `python3`.


### Create a Virtual Environment
```sh
python3 -m venv env
```

### Activate the environment

- On Windows (powershell)
    ```sh
    .\env\Scripts\Activate.Ps1
    ```

- On Windows (cmd)
    ```sh
    env\Scripts\activate.bat
    ```

- On Linux or macOS (or Git Bash in Windows)
    ```sh
    source env/bin/activate
    ```

### Install Required Libraries

```sh
python -m pip install -r requirements.txt
```

### Compiling UI and Resource Files

```sh
python compile.py
```

### Running

```sh
python src/main.py
```

## Change Version Number

```sh
python change-version.py NEW_VERSION
```


## Packaging

### Windows

Packaging for windows uses two tools. First, pyinstaller is used to create a minimal python distribution and an executable for the app from the python source. Then InnoSetup is used to create an installer for the program. Since pyinstaller is used, this process must be performed on a windows PC.

```shell
.\env\bin\activate
cd packaging
.\windows.cmd
```

### macOS

Packaging for macOS uses pyinstaller to create the app. The app is then zipped for distribution. Since pyinstaller is used, this process must be performed on a mac. Furthermore, building native apps for an arm (Apple Silicon) mac is currently not supported (at time of writing pyinstaller has support but some dependency python packages do not have native arm build for macOS available).

```shell
source env/bin/activate
cd packaging
./macos.sh
```

### Linux

Packaging for linux can be done one of two ways. The first way uses pyinstaller to create a binary. The second is by bundling the sources and using an installation script to setup a virtual environment.

The first method creates a program that has no system dependencies (aside from c runtime libraries), but is a large package. The second method creates a small package, but relies on the system having python3 installed.

Either method results in a package that can be compressed as a gzipped tarball or optionally turned into a distribution specific package (deb, rpm, etc).

#### PyInstaller Method

*To ensure compatibility with the most possible distributions, it is recommended to perform this build on an older linux distro (older glibc). Ubuntu 14.04 or 16.04 is recommended, however a newer version of python3 will likely be needed (either build from source or use unofficial ppa) as Pyside6 does not support anything older than python 3.6 (at time of writing). Since pyinstaller is used, this must be performed on a linux system.*

```shell
source env/bin/activate
cd packaging
./linux_pyinstaller.sh
```

#### Source Method

*This method is generally recommended as it produces smaller packages and is the most compatible across distributions.*

```shell
source env/bin/activate
cd packaging
./linux_source.sh
```
