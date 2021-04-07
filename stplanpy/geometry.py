import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection

def intersect(df1, df2):
# Workaround for geopandas < 0.9
    df = gpd.overlay(df1, df2, how="intersection", keep_geom_type=False)

    if not (df.empty):
        gtype = df.geom_type.values[0]
        if (gtype == "GeometryCollection"):
            
            geoms = []
            for geom in df["geometry"].values[0]:
                gtype = geom.geom_type
                if (gtype == "Polygon" or gtype == "MultiPolygon"):
                    geoms.append(geom)

            if (geoms):
                if (len(geoms) == 1):
                    geoms = geoms[0]
                else:
                    geoms = MultiPolygon(geoms)

# Overwrite geometry and gtype
                df["geometry"] = geoms
                gtype = df.geom_type.values[0]
    
    else:        
        gtype = None

# Only return of dataframe contains a (Multi)Polygon
    if (gtype == "Polygon" or gtype == "MultiPolygon"):
        return df
    else:
        return pd.DataFrame(columns=list(df.columns))

def corr_cent(lon, lat):
    
    corr = Point(lon, lat)
    corr = gpd.GeoDataFrame(geometry=[corr], crs="EPSG:4326")
    corr = corr.to_crs("EPSG:6933")

    return corr["geometry"].values[0]
