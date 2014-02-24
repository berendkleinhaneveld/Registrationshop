# Build instructions

This file contains the instructions for building and running RegistrationShop on OS X, Linux and Windows.


### Prerequisites

Please install Elastix by downloading it [here](http://elastix.isi.uu.nl/download.php). Binaries are available for all platforms. Make sure that it is reachable from your path. So you should be able to just run:

    elastix --help

Install pyyaml and pyside by running the following on OS X and Linux:

    sudo easy_install pyyaml
    sudo easy_install pyside

On Windows:

* Install Python 2.7
* Install PyYaml (packages available at http://pyyaml.org/wiki/PyYAML)
* Install PySide (https://qt-project.org/wiki/PySide_Binaries_Windows)


### Custom VTK

Download VTK at https://github.com/berendkleinhaneveld/VTK/tree/release and build with Cmake and make sure that Python wrappings are on.

After building VTK successfully, make sure you have the following system variables and make sure that they contain the following paths:

On OS X (add to ~/.profile) and Linux (add to ~/.bashrc):

__VTK_DIR:__

    {VTKBUILDDIR}

__PYTHONPATH:__

    {VTKBUILDDIR}/bin
    {VTKBUILDDIR}/lib
    {VTKBUILDDIR}/Wrapping/Python

__PATH:__

    {VTKBUILDDIR}/bin
    {VTKBUILDDIR}/Wrapping/Python
    {VTKBUILDDIR}/Wrapping/PythonCore

__LD_LIBRARY_PATH:__

    {VTKBUILDDIR}/bin

On Windows:

__VTK_DIR:__

    {VTKBUILDDIR}\bin\Release

__PYTHONPATH:__

    {VTKBUILDDIR}\Wrapping\Python
    {VTKBUILDDIR}\Wrapping\Python\vtk
    {VTKBUILDDIR}\bin\Release

__PATH:__

    {VTKBUILDDIR}\bin\Release
    C:\Python27

Note: it might be that not all paths are needed, but at least this configuration should work.

### RegistrationShop

Download RegistrationShop at https://github.com/berendkleinhaneveld/Registrationshop.

You should now be able to run:

    python RegistrationShop.py

Please send an email or open an issue if you have troubles with any of these steps: I'm happy to help out!
