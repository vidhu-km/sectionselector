import geopandas as gpd
import folium

gdf = gpd.read_file("ooipsectiongrid.shp")

# Ensure original CRS is set
if gdf.crs is None:
    raise ValueError("Missing CRS in shapefile")

# Reproject to a projected CRS (meters-based)
gdf_projected = gdf.to_crs(epsg=26913)

# Compute centroid in projected CRS (accurate)
centroid = gdf_projected.geometry.centroid

# Convert centroids back to lat/lon
centroid_latlon = gpd.GeoSeries(centroid, crs=26913).to_crs(epsg=4326)

center = [centroid_latlon.y.mean(), centroid_latlon.x.mean()]

# Back to lat/lon for mapping
gdf = gdf.to_crs(epsg=4326)

# Create map
m = folium.Map(location=center, zoom_start=10)

# Fields (exclude geometry)
fields = [col for col in gdf.columns if col != "geometry"]

# Add layer
folium.GeoJson(
    gdf,
    tooltip=folium.GeoJsonTooltip(fields=fields),
    style_function=lambda x: {
        "color": "blue",
        "weight": 1,
        "fillOpacity": 0.3
    }
).add_to(m)

m.save("map.html")

print("Map saved as map.html")