import gdal
import os

def ras2heat(raster, outdir):
    """
    Displays data from an input raster as an interactive web map by converting it to a heatmap and displaying with the Google Maps API

    :param raster: input raster
    :param outdir: directory to write webpage outputs

    :return: 0 on fail, 1 on success

    """
    success = 0
    return success