# LabelLib

## General description
LabelLib is a library for the simulation of small probes flexibly coupled to biomolecules. Such probes are for instance dyes for fluorescence spectroscopy, spin-labels for EPR and NMR, or chemical cross-links for mass-spectrometry. 

LabelLib uses a coarse-grained approach to simulate the spatial distribution of probes around their attachment point. In this coarse-grained approach LabelLib determines the sterically accessible volume of the probe considering the linker length and the spatial dimensions of the probe. The linker connecting the probe to the biomolecule and the probe are approximated by a tube and ellipsoids, respectively. Details are provided in the publications [![DOI for citing FPS](https://img.shields.io/badge/DOI-10.1038%2Fnmeth.2222-blue.svg)](https://doi.org/10.1038/nmeth.2222)
[![DOI for citing FPS](https://img.shields.io/badge/DOI-10.1021%2Fja105725e-blue.svg)](https://doi.org/10.1021/ja105725e).


LabelLib is mainly intented to be used by programmers and provides APIs for C/C++ and Python. Furthermore, LabelLib can be integrated into PyMOL installations as described below. This allows to vizualize the distributions of molecular probes.

![dsDNA and an AV surface][2]

# Building and installation

## C++ shared library

C++ shared library can be installed from source with cmake:
```bash
git clone --recursive https://github.com/Fluorescence-Tools/LabelLib.git
mkdir LabelLib/build
cd LabelLib/build
cmake ..
sudo make install
```
On Linux you can build and install a package instead (prefered):
```bash
...
cmake .. && make package
sudo dpkg -i FlexLabel-*-Linux.deb
```

## Python bindings

Python bindings can be installed via pip. Installation of the C++ library is not necessary for this.
```bash
sudo pip install LabelLib
```

# Usage

## Pymol

To access the functionality of LabelLib in PyMOL two basic prerequisites need to be fulfilled:
  1) LabelLib needs to be installed in the Python installation used by PyMOL
  2) The file [LabelLib_pymol.py](FlexLabel/python/LabelLib_pymol.py) needs to be downloaded and executed from PyMOL's command line interace. 
  
The file "LabelLib_pymol.py" is executed from PyMOL's command line interface by entering "run LabelLib_pymol.py". Once "LabelLib_pymol.py" is executed Accessible Volumes(AV) can be simulated from PyMOL's command line. The procedure of running "LabelLib_pymol.py" and simulating an AV is shown below for an example:
```
cmd.do('run ./LabelLib/FlexLabel/python/LabelLib_pymol.py')
cmd.fetch('1BNA', async=0)
genAV(obstacles='1BNA and not solvent and not (c. B and i. 19 and name C7+C4+O4+C6)', attachment='1BNA and c. B and i. 19 and name C5', linker_length=20.0, linker_diameter=2.0, dye_radius=3.5)
```
As a result you should see something like this:

![dsDNA and an AV surface][2]

## C++

C++ usage example can be found in [testFlexLabel.cxx](FlexLabel/test/testFlexLabel.cxx). Your own software could be compiled like this:
```bash
cd LabelLib/FlexLabel/test
g++ -std=c++14 -O3 -o FlexLabelTest testFlexLabel.cxx -lFlexLabel
./FlexLabelTest
```
Possible output:
> AV calculation took: 20.783 ms

## Python

The LabelLib can be used from python as shown below in a code example.
LabelLib requires the Cartesian-coordinates, xyz, and van der Waals radii, vdW, of the biomolecule the label is attached to. The Cartesian coordinates and the vdW radii are passed to LabelLib as a single array (see example below). 
```python
import LabelLib as ll
import numpy as np
atoms = np.zeros((4,11))
linker_length = 20.0
linker_width = 2.0
dye_radius = 3.5
simulation_grid_spacing = 0.9
dye_attachment_point = np.zeros(3)
av1 = ll.dyeDensityAV1(atoms, dye_attachment_point, linker_length, linker_width, dye_radius, simulation_grid_spacing)

# The object av1 has the property grid, which stores
# the distances to the attachment point within the reach of the dye linker 
# as a positive number. For points out of out reach of the linker, the the 
# grid contains negative numbers.
grid = av1.grid

# The shape of the grid is defined by the property '.shape'
shape = av1.shape

# The 3D grid is a flat 1D python list in 'Fortran' order
grid3d = np.array(grid).reshape(shape, order='F')

```
Another usage example is available in [usage.py](FlexLabel/python/usage.py)

# Citation
If you have used LabelLib in a scientific publication, we would appreciate citations to the following paper: [![DOI for citing LabelLib](https://img.shields.io/badge/DOI-10.1016%2Fj.sbi.2016.11.012-blue.svg)](https://doi.org/10.1016/j.sbi.2016.11.012)
> Dimura, M., Peulen, T.O., Hanke, C.A., Prakash, A., Gohlke, H. and Seidel, C.A., 2016. Quantitative FRET studies and integrative modeling unravel the structure and dynamics of biomolecular systems. Current opinion in structural biology, 40, pp.163-185.

Additional information is available in FPS toolkit paper: [![DOI for citing FPS](https://img.shields.io/badge/DOI-10.1038%2Fnmeth.2222-blue.svg)](https://doi.org/10.1038/nmeth.2222)
> Kalinin, S., Peulen, T., Sindbert, S., Rothwell, P.J., Berger, S., Restle, T., Goody, R.S., Gohlke, H. and Seidel, C.A., 2012. A toolkit and benchmark study for FRET-restrained high-precision structural modeling. Nature methods, 9(12), pp.1218-1225.

[1]: https://pymol.org/ "Pymol"
[2]: FlexLabel/doc/pymol_example.png "dsDNA and an AV surface"
