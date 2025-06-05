import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper
import geopandas as gpd

# Load data
data = pd.read_csv('https://github.com/sawsannn/Data-Visualization-of-Indonesia-Rice-Production/blob/main/Data_Tanaman_Padi_Sumatera_version_1.csv?raw=true')
data.set_index('Tahun', inplace=True)

# Unique provinces
prov_list = data.Provinsi.unique().tolist()

# Define color palette and mapper
custom_palette = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # gray
]

color_mapper = CategoricalColorMapper(factors=prov_list, palette=custom_palette)

# Rename columns for ease of use
data.rename(columns={'Suhu rata-rata':'suhu_rata','Curah hujan':'curah_hujan','Luas Panen':'luas_panen'}, inplace=True)

# Create initial ColumnDataSource for 1993
source = ColumnDataSource(data={
    'x'       : data.loc[1993].Produksi,
    'y'       : data.loc[1993].luas_panen,
    'provinsi': data.loc[1993].Provinsi,
})

# Create scatter plot figure
plot = figure(title='Year: 1993', x_axis_label='Jumlah Produksi', y_axis_label='Luas Panen',
              height=400, width=700)
hover = HoverTool(tooltips=[("Provinsi", "@provinsi")])
plot.add_tools(hover)

# Scatter plot circles
plot.circle(x='x', y='y', source=source, fill_alpha=0.8,
            color=dict(field='provinsi', transform=color_mapper), legend_label='provinsi')
plot.legend.location = 'top_right'

# Streamlit widgets for interaction
st.header("Scatter Plot Controls")
slider = st.slider('Year', 1993, 2020, 1993, 1)
x_select = st.selectbox('Select x-axis data', ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata'], index=0)
y_select = st.selectbox('Select y-axis data', ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata'], index=1)

# Update function for scatter plot
def update_plot(year, x_col, y_col):
    plot.xaxis.axis_label = x_col
    plot.yaxis.axis_label = y_col
    
    new_data = {
        'x': data.loc[year][x_col],
        'y': data.loc[year][y_col],
        'provinsi': data.loc[year]['Provinsi']
    }
    source.data = new_data
    plot.title.text = f'Year: {year}'

update_plot(slider, x_select, y_select)

# Show scatter plot
st.bokeh_chart(plot)

# Load GeoJSON for Indonesian provinces
gdf = gpd.read_file("https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.geojson")

# Rename to match data
gdf = gdf.rename(columns={'propinsi': 'Provinsi'})

# Prepare 2020 data for merging
data_2020 = data.loc[2020].reset_index()

# Merge GeoDataFrame with data
gdf = gdf.merge(data_2020, on='Provinsi', how='inner')

# Extract polygon coordinates for Bokeh
def extract_coords(poly):
    if poly.geom_type == 'MultiPolygon':
        xs = [list(p.exterior.coords.xy[0]) for p in poly.geoms]
        ys = [list(p.exterior.coords.xy[1]) for p in poly.geoms]
    else:
        xs = [list(poly.exterior.coords.xy[0])]
        ys = [list(poly.exterior.coords.xy[1])]
    return xs, ys

gdf['x'], gdf['y'] = zip(*gdf.geometry.apply(extract_coords))

# Create ColumnDataSource for geo plot
geo_source = ColumnDataSource(gdf)

# Create geospatial plot
geo_plot = figure(
    title='Peta Produksi Padi per Provinsi (2020)',
    x_axis_label='Longitude',
    y_axis_label='Latitude',
    plot_width=700,
    plot_height=500,
    tools='pan,wheel_zoom,reset,hover',
    tooltips=[("Provinsi", "@Provinsi"), ("Produksi", "@Produksi")]
)

# Draw province patches
geo_plot.patches('x', 'y', source=geo_source, fill_alpha=0.7,
                 fill_color='lightgreen', line_color='black', line_width=0.5)

# Subtitle and map
st.subheader("Peta Geospasial - Data Tahun 2020")
st.bokeh_chart(geo_plot)
