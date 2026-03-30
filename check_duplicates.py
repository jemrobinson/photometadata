#! /usr/bin/env python
from glob import glob
from pathlib import Path

f_temporary = Path.home() / "Library" / "CloudStorage" / "OneDrive-Personal"
f_permanent = Path.home() / "Syncthing" / "Photos"

print(f_temporary)
for filename in glob(f"{f_temporary}/**/*.jpg", recursive=True):
    print(filename, type(filename))
