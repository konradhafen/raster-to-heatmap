from osgeo import gdal, ogr, osr
import numpy as np
import os

def ras2heat(raster, outdir):
    """
    Displays data from an input raster as an interactive web map by converting it to a heatmap and displaying with the Google Maps API

    :param raster: path to input raster
    :param outdir: directory to write webpage outputs

    :return: 0 on fail, 1 on success

    """
    success = 1
    setupOutdir(outdir)
    ras2js(raster, outdir)
    return success

def setupOutdir(outdir):
    """
    Setup file structure in output directory

    :param outdir: path to output directory

    :return: None

    """
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    if not os.path.exists(outdir + "/webmap"):
        os.mkdir(outdir + "/webmap")
    if not os.path.exists(outdir + "/webmap/assets"):
        os.mkdir(outdir + "/webmap/assets")
    if not os.path.exists(outdir + "/webmap/assets/css"):
        os.mkdir(outdir + "/webmap/assets/css")
    if not os.path.exists(outdir + "/webmap/assets/js"):
        os.mkdir(outdir + "/webmap/assets/js")
    # if not os.path.exists(outdir + "/webmap/assets/data"):
    #     os.mkdir(outdir + "/webmap/assets/data")

def ras2js(raster, outdir):
    """
    Converts raster cells containing data to geojson which is used to create a heatmap.
    :param raster:
    :param outdir:

    :return: 0 on fail, 1 on success.

    """
    success = 1
    ds = gdal.Open(raster)
    array = ds.GetRasterBand(1).ReadAsArray()
    nodata = ds.GetRasterBand(1).GetNoDataValue()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    geot = ds.GetGeoTransform()
    transform = getCoordinateTransformation(srs)
    addresses = getDataAddresses(array, nodata)
    json = open(outdir + "/webmap/assets/data/raster.geojson", 'w') #create geojson file
    json.write("eqfeed_callback({\"type\":\"FeatureCollection\",\n \"features\": [\n") #write first line

    count = 0
    for address in addresses:
        count += 1
        coords = getCoordinatesOfCellAddress(address[0], address[1], geot) #get coordinates of cell addresses
        point = ogr.CreateGeometryFromWkt("POINT (" + str(coords[0]) + " " + str(coords[1]) + ")") #create OGR point
        point.Transform(transform) #transform from raster coordinate system to WGS84
        json.write("{\"type\": \"Feature\", \"geometry\": {\"type\": \"Point\", \"coordinates\": [" + str(point.GetX())
                   + " " + str(point.GetY()) + "]}, \"properties\": {\"value\": " + str(array[address[0], address[1]])
                   + "}}") #write json feature data
        if count < len(addresses):
            json.write(",\n") #do not print comma for last item

    json.write("]});") #close of function, feature, collection, and features
    json.close() #close file
    ds = None
    return success

def getDataAddresses(array, nodata):
    """
    Get addresses of cells containing data

    :param array: numpy array of raster data.
    :param nodata: NoData value.

    :return: numpy array (n row, 2 column) of cell addresses.

    """
    return np.swapaxes(np.where(array <> nodata), 0, 1)

def getCoordinatesOfCellAddress(row, col, geot):
    """
    Calculate the coordinate pair at the center of a cell address based on the input DEM. UTM projections suggested, will not work with degree units.

    :param row: Row index of the raster.
    :param col: Column index of the raster.
    :param geot: GDAL geotransform for the raster.

    :return: numpy array with x and y coordinates (array[x, y]).
    """
    x = geot[0] + (col * geot[1]) + (0.5 * geot[1])
    y = geot[3] + (row * geot[5]) + (0.5 * geot[5])
    coords = np.array([x, y])
    return coords

def getCoordinateTransformation(srs):
    """
    Get object to transform coordinates from raster coordinate system to WGS84.

    :param srs: Coordinate system of raster.

    :return: Coordinate transformation object.

    """
    srstarget = osr.SpatialReference()
    srstarget.SetWellKnownGeogCS("WGS84")
    transform = osr.CoordinateTransformation(srs, srstarget)
    return transform
