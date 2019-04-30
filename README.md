# peleg-tracker 

a command line interface to interact with bee tracking software written in support of the research conducted in Peleg Lab at the University of Colorado, Boulder. 

## 

### dependencies 

this code was written in python3 and depends on the following standard python packages.

> opencv2, matplotlib, skimage, numpy 

instructions for installing python3 [here](https://realpython.com/installing-python/) and pip [here](https://pip.pypa.io/en/stable/installing/).

once python3 and pip are installed run the following command from the command line.

```
pip install opencv-python matplotlib scikit-image numpy
```

if this runs with no errors you are ready to go!

##

### usage

this object you will be interacting with is a workspace. each workspace must have a unique name and a number of files will be automatically generated. this is to help keep different configurations and tracking instances seperate. when this repository is first cloned their will be a directory named workspaces with a single file in it

```
project
│   README.md
│       
└─── workspaces 
│   │   __init__.py
│   │   file012.txt
│   
└─── bin
    │   ...
```
