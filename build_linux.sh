#!/usr/bin/env bash

DIR=$(realpath $(dirname "$0"))

pushd "$DIR"

if [[ -f env/ ]]; then
    rm -rf env/
fi

if [[ -f dist/ ]]; then
    rm -rf dist/
fi

python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
python -m pip install cx_Freeze
python compile.py
python setup.py build --build-exe dist/CFModpackImporter
cd dist
zip -q -r CFModpackImporter_Linux64.zip CFModpackImporter/
cd ..

popd
