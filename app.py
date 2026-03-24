import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Polygon Selector")

# Load shapefile
gdf = gpd.read_file("ooipsectiongrid.shp")

# Ensure CRS is lat/lon
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Add ID column
gdf = gdf.reset_index().rename(columns={"index": "id"})

# Store selected polygons
if "selected" not in st.session_state:
    st.session_state.selected = set()

# Center map
centroid = gdf.geometry.centroid
center = [centroid.y.mean(), centroid.x.mean()]

m = folium.Map(location=center, zoom_start=10)

# Style function
def style_function(feature):
    idx = feature["properties"]["id"]
    if idx in st.session_state.selected:
        return {"color": "red", "weight": 3, "fillOpacity": 0.5}
    return {"color": "blue", "weight": 1, "fillOpacity": 0.2}

# JavaScript click handler
click_js = """
function(feature, layer) {
    layer.on('click', function(e) {
        // Send clicked feature id back to Streamlit
        window.parent.postMessage({
            "type": "folium_click",
            "id": feature.properties.id
        }, "*");
    });
}
"""

geo = folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=[col for col in gdf.columns if col != "geometry"]
    ),
    on_each_feature=click_js
)

geo.add_to(m)

# Render map
map_data = st_folium(m, height=600, width=800)

# Capture click from message
if map_data and "last_object_clicked" in map_data:
    clicked = map_data["last_object_clicked"]

    if clicked and "id" in clicked:
        clicked_id = clicked["id"]

        if clicked_id in st.session_state.selected:
            st.session_state.selected.remove(clicked_id)
        else:
            st.session_state.selected.add(clicked_id)

# Show selected polygons
if st.session_state.selected:
    selected_df = gdf[gdf["id"].isin(st.session_state.selected)]

    st.write("Selected polygons:")
    st.dataframe(selected_df.drop(columns="geometry"))

    csv = selected_df.drop(columns="geometry").to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        file_name="selected_polygons.csv",
        mime="text/csv"
    )