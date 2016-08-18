"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/CFSR
"""
# General modules
import os
import subprocess

def Convert_grib2_to_netCDF(Date,local_filename,output_folder,i):
    """
    This function converts .grib2 (WHO standard) to netcdf using gdal's gdal_translate function

    Keyword arguments:
    Date -- pandas timestamp day
    local_filename -- The path to the .grib data
    output_folder -- The directory for the .nc output
    i -- 1...4 period of the day
    """
	# The .nc output name
    nameNC = 'Output' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + str(Date.strftime('%d')) + '-' + str(i+1) + '.nc'
				
    # Total path of the output 				
    FileNC6hour = os.path.join(output_folder, nameNC)
				
	# Band number of the grib data which is converted in .nc			
    band=(int(Date.strftime('%d')) - 1) * 28 + (i + 1) * 7
				
	# converting			
    fullCmd = ' '.join(['gdal_translate -of netcdf -b %d' %(band), local_filename, FileNC6hour])  # -r {nearest}
    process = subprocess.Popen(fullCmd)
    process.wait()  