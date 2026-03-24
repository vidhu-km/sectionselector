import geopandas as gpd
import folium

# Load shapefile
gdf = gpd.read_file("ooipsectiongrid.shp")

# Ensure CRS is lat/lon
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Add ID
gdf = gdf.reset_index().rename(columns={"index": "id"})

# Center map
centroid = gdf.geometry.centroid
center = [centroid.y.mean(), centroid.x.mean()]

m = folium.Map(location=center, zoom_start=10)

# Style function
def style_function(feature):
    return {
        "color": "blue",
        "weight": 1,
        "fillOpacity": 0.3,
    }

# Add GeoJson with click behavior
geo = folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=[col for col in gdf.columns if col != "geometry"]
    )
)

geo.add_to(m)

# Add JavaScript for click-to-toggle highlight
click_js = """
function(e) {
    var layer = e.target;

    if (layer.selected) {
        layer.setStyle({color: 'blue', fillOpacity: 0.3});
        layer.selected = false;
    } else {
        layer.setStyle({color: 'red', fillOpacity: 0.6});
        layer.selected = true;
    }
}
"""

# Attach click handler to each feature
for feature in geo.data['features']:
    layer = folium.GeoJson(
        feature,
        style_function=style_function
    )
    layer.add_to(m)
    layer.add_child(folium.features.GeoJsonPopup(fields=list(gdf.columns)))
    layer.add_child(folium.GeoJsonTooltip(fields=list(gdf.columns)))
    layer.add_child(folium.Element(
        f"<script>{click_js}</script>"
    ))

# Save map
m.save("map.html")

print("Map saved as map.html. Open it in your browser.")