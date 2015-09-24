# Install RegistrationShop on Ubuntu

For creating this guide I've used a fresh install of Ubuntu 64 bit (15.04).

## Preparation

First prepare some development/installation folders:

```bash
cd ~/Documents
mkdir Development
cd Development
mkdir elastix

sudo apt-get install git
sudo apt-get install python-pip
sudo apt-get install build-essential git cmake libqt4-dev libphonon-dev python2.7-dev libxml2-dev libxslt1-dev qtmobility-dev
sudo apt-get install cmake-curses-gui # Needed for configuring VTK
sudo apt-get install libxt-dev        # Needed for building VTK

pip install -U pyyaml
pip install -U PySide  # Will take a while...
```

If installing PySide doesn't work, you can perform the next steps (steps from http://pyside.readthedocs.org/en/latest/building/linux.html):

```bash
wget https://pypi.python.org/packages/source/P/PySide/PySide-1.2.2.tar.gz
tar -xvzf PySide-1.2.2.tar.gz
cd PySide-1.2.2
python2.7 setup.py bdist_wheel --qmake=/usr/bin/qmake-qt4
pip install dist/PySide-1.2.2-cp27-none-linux_x86_64.whl
ldd ~/.local/lib/python2.7/site-packages/PySide/libpyside-python2.7.so.1.2
```

The last step prints the dependencies of the shared library. If you see something like 'file not found' behind the shiboken line, then you'll need to perform the following steps as well (source: http://stackoverflow.com/questions/18369516/pyside-import-error-on-ubuntu-13-04):

```bash
echo "$HOME/.local/lib/python2.7/site-packages/PySide" | sudo dd of=/etc/ld.so.conf.d/pyside.conf
sudo ldconfig
```

## Install Elastix

Extact to `~/Documents/Development/elastix`

Add `~/Documents/Development/elastix/bin` to path:

```bash
# Add export line to .bashrc
echo 'export PATH=~/Documents/Development/elastix/bin:$PATH' >> ~/.bashrc
# Reload .bashrc
. ~/.bashrc
```

You should now be able to run elastix.

## Install custom VTK

Clone a modified version of VTK with modifications needed for RegistrationShop's multi volume renderer.

```bash
git clone https://github.com/berendkleinhaneveld/VTK.git
git checkout origin/release

# Create build folder
mkdir VTKBuild
cd VTKBuild
# Start ccmake to configure build
ccmake ../VTK
```

Press `c` for configuring.

| CONFIG           | VALUE   |
|------------------|---------|
| BUILD_TESTING    | OFF     |
| CMAKE_BUILD_TYPE | Release |
| VTK_WRAP_PYTHON  | ON      |

Press `c` to configure for the change.
Press `c` again.
Press `g` to generate config.
See [here](http://www.vtk.org/Wiki/VTK/Configure_and_Build) for more info on building VTK.

```bash
make -j2
# The number after -j represents the number of threads that will be used for
# building VTK. Use it to your advantage ;)
```
Now go and get some coffee.

If you get error: `error: ‘GLintptr’ has not been declared`, set the `CMAKE_CXX_FLAGS` and `CMAKE_C_FLAGS` fields to:

    -DGLX_GLXEXT_LEGACY

http://stackoverflow.com/questions/28761702/getting-error-glintptr-has-not-been-declared-when-building-vtk-on-linux


## Install RegistrationShop

```bash
git clone https://github.com/berendkleinhaneveld/Registrationshop.git
cd Registrationshop
git submodule update --init --recursive
```

## Run RegistrationShop

```bash
python RegistrationShop.py
```

## Notes

If your Ubuntu install is running with open-source graphics drivers, your results may vary. If you encounter any problem with rendering volumes with RegistrationShop while using open-source graphics drivers, then please consider installing proprietary drivers of your graphics card vendor and rebuilding VTK.
