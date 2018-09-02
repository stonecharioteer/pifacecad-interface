# PiFaceCAD Interface

This project provides an interface for the Raspberry Pi 3B using 
the PiFaceCAD HAT module.

## TODO List:

- [x] Time Display
- [ ] Dynamic Backlight based on time and activity.
- [x] IP Address display.
- [ ] Temperature Scraper

## Installation & Setup

1. To install/run this interface, you need a PiFaceCAD Hat and a Raspberry Pi 3B.
2. Install python3-venv.
3. Create a virtualenv with `python3 -m venv env`
4. Activate the newly created virtual environment.
5. Download the `PiFACECommon` python package from the github repository, do not install the package using the raspbian repositories.
6. Download and install `PiFaceCAD` and `python-lirc` the same way. `python-lirc` requires installation of additional packages.
7. Install the rest of the requirements, and then run the script.

