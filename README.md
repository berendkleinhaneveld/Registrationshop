# Registrationshop

Interactive registration tool for 3D medical datasets.

![Screenshot of the Registrationshop user interface](https://github.com/berendkleinhaneveld/Registrationshop/assets/1000968/b8c9f144-914c-427d-8a59-33732cc3bb4c)

## Components
Written for the most part in Python. Uses PySide for the interface and uses VTK for the visualizations. Uses [vtkMultiVolRen](https://github.com/karlkrissian/vtkMultiVolRen) for rendering multiple datasets in one vtkRenderer. My fork can be found at [https://github.com/berendkleinhaneveld/vtkMultiVolRen](https://github.com/berendkleinhaneveld/vtkMultiVolRen). Because of issues with building that fork on Windows I've incorporated the code into a fork of VTK which can be found at [https://github.com/berendkleinhaneveld/VTK/tree/release](https://github.com/berendkleinhaneveld/VTK/tree/release). Besides multi-volume render capabilities there are also some other nice features planned to be added to VTK and Registrationshop real soon... But more on that later!

For deformable registration [elastix](http://elastix.isi.uu.nl) is used. The rigid transformation that you can create with the rigid registration tools will serve as initial transformation for elastix. The parameters for elastix can be edited inside Registrationshop so you don't have fall back to editing raw parameter files!

## Installation

On macOS, it is now possible to install with `conda`.

    conda env create
    conda activate registrationshop
    pythonw RegistrationShop.py

Note the 'w' after python: that is not a typo. Running with `python` will give the following error message:
    
    Qt internal error: qt_menu.nib could not be loaded.

Instructions on how to build Registrationshop are available [here](INSTRUCTIONS.md)! Let me know if you run into any troubles. For some platforms, builds are not available yet.

## Supported platforms
* OS X (Mountain Lion+)
* Linux (requires AMD/NVIDIA proprietary drivers)
* Windows
