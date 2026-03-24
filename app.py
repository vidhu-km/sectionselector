import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Polygon Selector")

# Load shapefile
gdf = gpd.read_file("ooipsectiongrid.shp")

# Ensure CRS is lat/lon for web maps
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Store selected indices
if "selected" not in st.session_state:
    st.session_state.selected = set()

# Center map
center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
m = folium.Map(location=center, zoom_start=10)

def style_function(feature):
    idx = feature["id"]
    if idx in st.session_state.selected:
        return {"color": "red", "weight": 3}
    return {"color": "blue", "weight": 1}

# Add polygons
geo = folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns))
)

geo.add_to(m)

# Capture clicks
map_data = st_folium(m, height=600, width=800)

# Handle click events
if map_data["last_active_drawing"]:
    clicked_idx = map_data["last_active_drawing"]["id"]

    if clicked_idx in st.session_state.selected:
        st.session_state.selected.remove(clicked_idx)
    else:
        st.session_state.selected.add(clicked_idx)

# Show selected attributes
if st.session_state.selected:
    selected_df = gdf.loc[list(st.session_state.selected)]

    st.write("Selected polygons:")
    st.dataframe(selected_df)

    csv = selected_df.drop(columns="geometry").to_csv(index=False)
    st.download_button(
        "Download CSV",
        csv,
        "selected_polygons.csv",
        "text/csv"
    )