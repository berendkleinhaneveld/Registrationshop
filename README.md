# Registrationshop

Interactive registration tool for 3D medical datasets.

![Screenshot of the Registrationshop user interface](https://graphics.tudelft.nl/wp-content/uploads/2013/09/maininterfacelungs.png)


## Components

Written in Python. Uses PySide for the interface and VTK for the visualizations.

For deformable registration [elastix](http://elastix.isi.uu.nl) is used. The rigid transformation that you can create with the rigid registration tools will serve as initial transformation for elastix. The parameters for elastix can be edited inside Registrationshop so you don't have fall back to editing raw parameter files!


## Installation

Make sure you have [poetry](https://python-poetry.org) installed, then perform the following:

```sh
poetry install
poetry run registrationshop
```


## Supported platforms

* macOS
* Linux
* Windows
