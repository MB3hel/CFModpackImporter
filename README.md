# CFModpackImporter

This tool is used to automate downloading of CurseForge mods for a modpack without using CurseForge's API. This is acheived by automating download tasks using a browser installed on the system (chrome or firefox). You must still download the modpack zipfile manually. The modpack zip contains the information needed by this tool to generate a list of mod donwload links. These links will then be used to automatically download mods. The modpack zip also incldues configs, resource packs, and other things needed by the modpack. These, along with downloaded mods, are then zipped into a single file. The contents of this resultant zip are able to be added to a modded instance to turn a modded instance into the modpack in question.

This tool will download and execute tools from [CFModDownloader](https://github.com/MB3hel/CFModDownloader) when run.


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
python -m pip install -U -r requirements.txt
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

