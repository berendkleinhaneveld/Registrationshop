# Registrationshop

Interactive registration tool for 3D medical datasets.

![Screenshot of the Registrationshop user interface](https://graphics.tudelft.nl/wp-content/uploads/2013/09/Registrationshop-2013-09-16.png)

Written for the most part in Python. Uses PySide for the interface and uses VTK for the visualizations. Uses [vtkMultiVolRen](https://github.com/karlkrissian/vtkMultiVolRen) for rendering multiple datasets in one vtkRenderer. My fork can be found at [https://github.com/berendkleinhaneveld/vtkMultiVolRen](https://github.com/berendkleinhaneveld/vtkMultiVolRen). Needs to be compiled first before Registrationshop can be made to work.

For deformable registration it uses [elastix](http://elastix.isi.uu.nl). The rigid transformation that you can create with the rigid registration tools will serve as initial transformation for elastix. The parameters for elastix can be edited inside Registrationshop so you don't have fall back to editing raw parameter files!

Instructions on how to make it build and run are not available yet: once the project is in a more functional state I will make sure to create a nice guide. Or maybe even create some builds? Who knows!
