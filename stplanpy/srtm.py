r"""
This module performs operations on the Digital Elevation Model (DEM) from the
NASA Shuttle Radar Topographic Mission (`SRTM`_).

.. _SRTM: https://srtm.csi.cgiar.org/
"""
import os
import glob
import shutil
import zipfile
#import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterstats import point_query

def reproj(file_name_in, file_name_out, crs="EPSG:6933"):
    r"""
    Reproject a GeoTIFF file

    Read a GeoTIFF file, reproject it to another coordinate reference system
    (crs), and write it to disk. The default crs is "EPSG:6933".

    Parameters
    ----------
    file_name_in : str
        Name and path of the input GeoTIFF file.
    file_name_out : str
        Name and path of the output GeoTIFF file.
    crs : str, defaults to "EPSG:6933"
        The coordinate reference system (crs) of the output GeoTIFF file. 
 
    Returns
    -------
    None
    
    Examples
    --------
    The example data file, "`srtm_12_05.zip`_", can be downloaded from github.
 
    .. code-block:: python

        import os
        import shutil
        import zipfile
        from stplanpy import srtm

        # Extract to temporal location
        with zipfile.ZipFile("srtm_12_05.zip", "r") as zip_ref:
            zip_ref.extractall("tmp")

        # reproject GeoTIFF file and write to disk
        srtm.reproj("tmp/srtm_12_05.tif", "srtm_12_05_EPSG6933.tif")

        # Clean up tmp files
        shutil.rmtree("tmp")

    .. _srtm_12_05.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/srtm_12_05.zip
    """
# Reprojecting the GeoTIFF file
    with rasterio.open(file_name_in) as src:
        transform, width, height = calculate_default_transform(
            src.crs, crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": crs,
            "transform": transform,
            "width": width,
            "height": height
        })

        with rasterio.open(file_name_out, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=crs,
                    resampling=Resampling.nearest)

@pf.register_dataframe_method
def elev(points: gpd.GeoDataFrame, file_name, tmp_dir="tmp") -> gpd.GeoDataFrame:

    r"""
    Compute the elevation at the locations in the points GeoDataFrame

    Read a (zipped) GeoTIFF file, reproject it the right coordinate reference
    system (crs), and use it to compute the elevation at the locations give in
    the points GeoDataFrame.

    Parameters
    ----------
    points :    
        GeoDataFrame with points at which the elevation is computed.
    file_name : str
        Name and path of the (zipped) GeoTIFF file.
    tmp_dir : str, defaults to "tmp"
        Name of temporary directory to store reprojected GeoTIFF file and
        extract the zip archive to.  
 
    Returns
    -------
    pandas.DataFrame
        DataFrame with elevation data
    
    Examples
    --------
    The example data file, "`srtm_12_05.zip`_", can be downloaded from github.
 
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import srtm

        # Create GeoDaFrame with some points
        df = pd.DataFrame(
        {"tazce": ["00101565", "00101589", "00101488", "00101503", "00101594"],
        'coordinates': ["POINT(-11822098.758 4499746.118)", 
        "POINT(-11820711.661 4497355.121)", "POINT(-11820275.989 4496557.912)", 
        "POINT(-11826751.214 4506575.748)", "POINT(-11823373.407 4503632.347)"]})

        # Parse wkt format:
        df['coordinates'] = gpd.GeoSeries.from_wkt(df['coordinates'])

        # Create GeoDataFrame
        points = gpd.GeoDataFrame(df, geometry="coordinates")

        # Set coordinate reference system (crs)
        points = points.set_crs("EPSG:6933")

        # Compute elevation at points
        points = points.elev("srtm_12_05.zip")

    .. _srtm_12_05.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/srtm_12_05.zip
    """
# Create temporary directory    
    os.makedirs(tmp_dir, exist_ok=True)

# Split file_name into name and extension
    name, extension = os.path.splitext(file_name)
# Name and path of reprojected GeoTIFF file.
    tmp_file = tmp_dir + "/" + os.path.basename(name) + ".tiff"

    if (extension == ".zip"):
        # Extract to temporal location
        with zipfile.ZipFile(file_name, "r") as zip_ref:
             zip_ref.extractall(tmp_dir)

        # find shape file
        tif_file = glob.glob("tmp/**/*.tif", recursive=True)
        if (len(tif_file) == 0):
            raise Exception("There is no tif file inside this zip archive")
        elif (len(tif_file) > 1):
            raise Exception("There is more than one tif file inside this zip archive")
    else:
        tif_file = [file_name]

# Reprojecting the GeoTIFF file
    reproj(tif_file[0], tmp_file, crs=points.crs)

# Compute elevation and create dataframe
#    elev = point_query(points, tmp_file)
    points["elevation"] = point_query(points, tmp_file)

# Clean up files
    shutil.rmtree(tmp_dir)
                                    
#    return pd.DataFrame(elev, columns = ["elevation"], index=points.index)
    return points
