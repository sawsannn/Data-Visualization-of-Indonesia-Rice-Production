import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper
import geopandas as gpd

# Load CSV data and set 'Tahun' as index
data = pd.read_csv(
    'https://github.com/sawsannn/Data-Visualization-of-Indonesia-Rice-Production/blob/main/Data_Tanaman_Padi_Sumatera_version_1.csv?raw=true'
)
data.set_index('Tahun', inplace=True)

# Unique provinces for color mapping
prov_list = data.Provinsi.unique().tolist()

# Color palette and mapper
custom_palette = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
]
color_mapper = CategoricalColorMapper(factors=prov_list, palette=custom_palette)

# Rename columns for easier reference
data.rename(columns={
    'Suhu rata-rata': 'suhu_rata',
    'Curah hujan': 'curah_hujan',
    'Luas Panen': 'luas_panen'
}, inplace=True)

# Streamlit header
st.title("Indonesia Rice Production Visualizations")

# --- Scatter Plot ---

# Initial data source for year 1993
def get_source(year, x_col, y_col):
    df = data.loc[year]
    return ColumnDataSource(data={
        'x': df[x_col],
        'y': df[y_col],
        'provinsi': df['Provinsi']
    })

# Widgets
st.header("Scatter Plot Controls")
year = st.slider('Year', min_value=1993, max_value=2020, value=1993, step=1)
x_axis = st.selectbox('X-axis data', ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata'], index=0)
y_axis = st.selectbox('Y-axis data', ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata'], index=1)

source = get_source(year, x_axis, y_axis)

scatter_plot = figure(
    title=f'Year: {year}',
    x_axis_label=x_axis,
    y_axis_label=y_axis,
    height=400,
    width=700,
    tools="pan,wheel_zoom,reset,hover"
)

hover = scatter_plot.select_one(HoverTool)
hover.tooltips = [("Provinsi", "@provinsi"), (x_axis, "@x"), (y_axis, "@y")]

scatter_plot.circle(
    x='x', y='y', source=source, size=10, fill_alpha=0.8,
    color={'field': 'provinsi', 'transform': color_mapper},
    legend_label='provinsi'
)

scatter_plot.legend.location = "top_right"
# scatter_plot.legend.title = "Provinsi"

st.bokeh_chart(scatter_plot)

# --- Geospatial Map ---

st.header("Geospatial Map for Year 2020")

# Load GeoJSON
gdf = gpd.read_file("https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.geojson")

# Rename to match your data column
gdf = gdf.rename(columns={'propinsi': 'Provinsi'})

# Prepare 2020 data for merging
data_2020 = data.loc[2020].reset_index()

# Merge geodataframe with 2020 data
gdf_merged = gdf.merge(data_2020, on='Provinsi', how='inner')

# Extract polygon coordinates for patches
def extract_coords(poly):
    if poly.geom_type == 'MultiPolygon':
        xs = [list(p.exterior.coords.xy[0]) for p in poly.geoms]
        ys = [list(p.exterior.coords.xy[1]) for p in poly.geoms]
    else:
        xs = [list(poly.exterior.coords.xy[0])]
        ys = [list(poly.exterior.coords.xy[1])]
    return xs, ys

gdf_merged['x'], gdf_merged['y'] = zip(*gdf_merged.geometry.apply(extract_coords))

geo_source = ColumnDataSource(gdf_merged)

geo_plot = figure(
    title='Peta Produksi Padi per Provinsi (2020)',
    x_axis_label='Longitude',
    y_axis_label='Latitude',
    plot_width=700,
    plot_height=500,
    tools='pan,wheel_zoom,reset,hover'
)

geo_plot.patches(
    'x', 'y', source=geo_source,
    fill_alpha=0.7,
    fill_color='lightgreen',
    line_color='black',
    line_width=0.5
)

geo_hover = geo_plot.select_one(HoverTool)
geo_hover.tooltips = [("Provinsi", "@Provinsi"), ("Produksi", "@Produksi")]

st.bokeh_chart(geo_plot)
