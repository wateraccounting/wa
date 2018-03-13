# WaterPix

WaterPix is a hydrologic data-based model used to perform water balances at a pixel scale.

## How to use the code

### Before you start

There are two software options to run WaterPix on python:
- [gdal](https://pypi.python.org/pypi/GDAL)
- [arcpy](http://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy/what-is-arcpy-.htm)

The two options are equivalent, the only difference is about the underlying library to process the geospatial data.

### Requirements
- Python 2.7, preferably the [Anaconda](https://www.continuum.io/downloads) 64-bit distribution
- Python libraries:
    - scipy ([https://pypi.python.org/pypi/scipy](https://pypi.python.org/pypi/scipy))
    - netCDF4 ([https://pypi.python.org/pypi/netCDF4](https://pypi.python.org/pypi/netCDF4))
    - pandas ([https://pypi.python.org/pypi/pandas](https://pypi.python.org/pypi/pandas))
    - rpy2 ([https://pypi.python.org/pypi/rpy2](https://pypi.python.org/pypi/rpy2))
- R 3.2.5 ([https://cran.r-project.org/](https://cran.r-project.org/))
- R packages:
    - sp ([https://cran.r-project.org/web/packages/sp/index.html](https://cran.r-project.org/web/packages/sp/index.html))
    - gstat ([https://cran.r-project.org/web/packages/gstat/index.html](https://cran.r-project.org/web/packages/gstat/index.html))
    - automap ([https://cran.r-project.org/web/packages/automap/index.html](https://cran.r-project.org/web/packages/automap/index.html))
- Additional:
    - *gdal* option
        - Python GDAL package ([https://pypi.python.org/pypi/GDAL](https://pypi.python.org/pypi/GDAL))
    - *arcpy* option
        - ArcMap software ([http://desktop.arcgis.com/en/arcmap/](http://desktop.arcgis.com/en/arcmap/))

### Installation

1. Identify a folder in your computer that is recognized by python (e.g. *...\Lib\site-packages*). You can check which folders are recognized by python with the following commands:
    ```python
    >>> import sys
    >>> sys.path
    ['',
    'C:\\Program Files\\Anaconda2\\lib\\site-packages',
    ...
    ```
1. Download or clone the *waterpix* module from the [online repository](https://github.com/gespinoza/waterpix) and place it into the folder recognized by python. 
    - Download: https://github.com/gespinoza/waterpix/archive/master.zip
    - Clone: https://github.com/gespinoza/waterpix.git
1. Check that *waterpix* works and that all the required modules are installed.
    - gdal
        ```python
        >>> from waterpix import wp_gdal
        >>> wa_gdal.__all__
        ['create_input_nc', 'run', 'output_nc_to_tiffs']
        ```
    - arcpy
        ```python
        >>> from waterpix import wp_arcpy
        >>> wa_gdal.__all__
        ['create_input_nc', 'run', 'output_nc_to_tiffs']
        ```
    **Note:** If you get the following error:
    ```python
    ImportError: No module named ...
    ```
    install the required modules, restart the python console, and repeat this step.

### Example

```python
from waterpix import wp_gdal

# Create input netcdf file
wp_gdal.create_input_nc(start_date='2010-01-01',
                        years=7,  # 2010 - 2016
                        cellsize=0.01078
                        basin_shp = r'C:\Temp\Basin_A.shp',
                        p_path = r'C:\Precipitation\chirps-v2.0_monthly_{yyyy}{mm}.tif',
                        et_path = r'C:\Evapotranspiration\L1_AET_{yyyy}{mm}.tif',
                        eto_path = r'C:\ReferenceET\ETref_mm-month-1_monthly_{yyyy}.{mm}.01.tif',
                        lai_path = r'C:\LeafAreaIndex\LAI_{yyyy}{mm}.tif',
                        swi_path = r'C:\Soil Moisture\MonthlyMean\SWI_{yyyy}{mm}.tif',
                        swio_path = r'C:\Soil Moisture\FirstDay\SWI_{yyyy}{mm}.tif',
                        swix_path = r'C:\Soil Moisture\LastDay\SWI_{yyyy}{mm}.tif',
                        qratio_path = r'C:\Runoff Ratio\Qr_{yyyy}.tif',
                        rainydays_path = r'C:\Rainy days\chirps-v2.0.{yyyy}.{mm}_rainydays.tif',
                        thetasat_ras = r'C:\Saturated water content\wcsat_topsoil.tif',
                        rootdepth_ras = r'C:\Root depth\rd_mm.tif',
                        input_nc = r'C:\input_file_basin_A.nc')

# Run WaterPix
input_nc = r'C:\input_file_basin_A.nc'
output_nc=r'C:\output_file_basin_A.nc'
wp_gdal.run(input_nc, output_nc)

# Export rasters
output_path = r'C:\output_rasters'
wp_gdal.output_nc_to_tiffs(output_nc, output_path)

```

## Citation
> Espinoza-Dávalos, G. E., & Bastiaanssen, W. G. M. (2017). *WaterPix: A Data Based Water Balance Model for Water Accounting.* http://doi.org/10.5281/zenodo.1045574

## Contact

**Gonzalo E. Espinoza, PhD, MSc**  
Integrated Water Systems and Governance  
IHE Delft Institute for Water Education  
T: [+31 15 2152313](tel:+31152152313)  
E: [g.espinoza@un-ihe.org](mailto:g.espinoza@un-ihe.org)  
I: [un-ihe.org](http://un-ihe.org) | [wateraccounting.org](http://wateraccounting.org) | [gespinoza.org](http://gespinoza.org)  

