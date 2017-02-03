# Water Accounting Plus Toolbox  ![](figs/wa_logo.png) 

_Independent estimates of water flows, fluxes, stocks, consumption, and services_

---

## <a name="About WA+"></a>About WA+

[Water Accounting Plus](http://wateraccounting.org/index.html) Water accounting is the process of communicating water resources related information and the services generated from consumptive use in a geographical domain, such as a river basin, a country or a land use class; to users such as policy makers, water authorities, managers, etc.

---

## <a name="Installation"></a>Installation

There are several packages available, which include python. The WA+ team recommends to download the python package of Anaconda. The great advantage of using the standard Anaconda package is that most of the commonly used modules are included in the package. Alternatively, these modules can be installed separately by the user if a different package than Anaconda is preferred.

### <a name="Install Anaconda"></a>Install Anaconda

Anaconda can be downloaded from: [http://continuum.io/downloads](http://continuum.io/downloads). It is recommended to download  the 64 bits version, because this will increase the calculation capacity enormously. However, be sure that your computer/laptop is a 64 bits computer/laptop.

The WA+ python codes are made for python version 2.7 for Windows operating systems. It is therefore necessary to download this version of python for running WA+ tools. Major changes are made to the python codes and functions if you compare 2.7 with 3+ versions. It is therefore not possible to run WA+ code in python 3+ versions without making some changes to the code.

![](figs/anaconda_install.png) 

After downloading Anaconda you can run the installation of Anaconda. This package also includes Spyder, which is the IDE (Integrated Development Environment). This is a layout for writing and running python scripts.

### <a name="How to install all the necessary Python modules"></a>How to install all the necessary Python modules

Modules are tools that can be imported into your python code. They usually contain stand-alone functions, which can be used within your own python code.

In order to import the Water Accounting Toolbox all the modules must be present. This can be checked by running the following line in Spyder:

>import wa

If you get no command everything is fine, else you will see:

>ImportError: No module named ... module name ...

Any missing modules can be installed by using one of the following four methods. 

#### <a name="Method 1"></a>Method 1

If a package is missing, you can search in the anaconda library by starting the command prompt and type:  

>conda install ... module name ...

This will only work if Anaconda is installed. Below is an example of a command to install the "gdal" module by using the Anaconda libary:

![](figs/module_install1.png) 

#### <a name="Method 2"></a>Method 2

You can also use the following command in the command prompt to install a module:

>pip install ... module name ...

Below is an example of a command to install the "pyproj" module by using the pip libary:

![](figs/module_install2.png) 

#### <a name="Method 3"></a>Method 3

It is also possible to install a module by using a .whl file (wheel-file). The wheels can be downloaded here: [http://pythonwheels.com/](http://pythonwheels.com/) and [http://www.lfd.uci.edu/~gohlke/pythonlibs/](http://www.lfd.uci.edu/~gohlke/pythonlibs/). Select the wheel containing win32 within the name if a 32 bits version of Python is used, and win_amd64 if the 64 bits version is used. After downloading the module wheel file, open command prompt and change the directory to the directory where the .whl file is located. You can change the directory in command prompt by using the cd command, as shown in the example below. 

![](figs/module_install3.png) 

After changing the directory, use the following command within the command prompt to install the module.

>pip install ... name.whl ... 

#### <a name="Method 4"></a>Method 4

If a module consists of a complete folder with a setup.py script inside after unzipping, the module can be installed by opening the command prompt and change the directory ("cd" command) to the path where the setup.py is located. Then you can install the module by using the following command within the command prompt:

>python setup.py install

---

## <a name="Functions"></a>Functions


---

## <a name="Troubleshoot"></a>Troubleshoot

jpeg2000 library missing (gebruik niet de gdal functies in anaconda omdat deze library hierin mist)
datum.csv  (gdal_data toevoegen)


---

>>>>>>> origin/master
