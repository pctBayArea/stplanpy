"""
https://srtm.csi.cgiar.org/
"""

import zipfile
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

def reproj(file_in, file_out, crs="EPSG:6933"):

# Reprojecting the GeoTIFF file
    with rasterio.open(file_in) as src:
        transform, width, height = calculate_default_transform(
            src.crs, crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": crs,
            "transform": transform,
            "width": width,
            "height": height
        })

        with rasterio.open(file_out, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=crs,
                    resampling=Resampling.nearest)
