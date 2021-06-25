r"""
This module performs operations on the Digital Elevation Model (DEM) from the
NASA Shuttle Radar Topographic Mission (`SRTM`_).

.. _SRTM: https://srtm.csi.cgiar.org/
"""

import zipfile
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

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
        The coordinate reference system (crs) of the output GeoTIFF file. The
        default value is "EPSG:6933".
 
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
        from stplanpy import elev

        # Extract to temporal location
        with zipfile.ZipFile("srtm_12_05.zip", "r") as zip_ref:
            zip_ref.extractall("tmp")

        # reproject GeoTIFF file and write to disk
        elev.reproj("tmp/srtm_12_05.tif", "srtm_12_05_EPSG6933.tif")

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
