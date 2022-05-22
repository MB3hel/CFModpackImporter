# CFModpackImporter

Download mods for curseforge modpacks and create a zip of files to be added to a modded instance in various third party launchers.


## Usage

Download the release for your OS and run the program. Follow instructions in `Help > Instructions`. **THIS DOES NOT CREATE AN INSTANCE IN ANY LAUNCHER**. It provides a zip that is to be added to the minecraft folder of an instance.

Fair warning: this is alpha quality software. It will have bugs, crashes, etc. It is intended as a proof of concept for downloading modpacks without CF API. 

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

