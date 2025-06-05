import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models import CategoricalColorMapper
from bokeh.palettes import Spectral6
from bokeh.layouts import row
from bokeh.models import Slider, Select
import geopandas as gpd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


data = pd.read_csv('https://github.com/sawsannn/Data-Visualization-of-Indonesia-Rice-Production/blob/main/Data_Tanaman_Padi_Sumatera_version_1.csv?raw=true')
data.set_index('Tahun', inplace=True)

prov_list = data.Provinsi.unique().tolist()

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

data.rename(columns={'Suhu rata-rata':'suhu_rata','Curah hujan':'curah_hujan','Luas Panen':'luas_panen'}, inplace=True)
# Create the ColumnDataSource: source
source = ColumnDataSource(data={
    'x'       : data.loc[1993].Produksi,
    'y'       : data.loc[1993].luas_panen,
    'provinsi'  : data.loc[1993].Provinsi,
})

# Create the figure: plot
plot = figure(title='1993', x_axis_label='Jumlah Produksi', y_axis_label='Luas Panen',
              plot_height=400, plot_width=700, tools='hover')
plot.add_tools(HoverTool(tooltips=[("Provinsi", "@provinsi")]))


# Create the scatter plot
plot.circle(x='x', y='y', source=source, fill_alpha=0.8,
           color=dict(field='provinsi', transform=color_mapper), legend='provinsi')

# Set the legend and axis attributes
plot.legend.location = 'top_right'

# Define the callback function: update_plot
def update_plot():
    yr = slider
    x = x_select
    y = y_select

    plot.xaxis.axis_label = x
    plot.yaxis.axis_label = y
    
    new_data = {
        'x': data.loc[yr][x],
        'y': data.loc[yr][y],
        'provinsi': data.loc[yr]['Provinsi']
    }
    
    source.data = new_data
    plot.title.text = 'Gapminder data for %d' % yr

# Create a slider object: slider
slider = st.slider('Year', 1993, 2020, 1993, 1)

# Create a dropdown Select widget for the x data: x_select
x_select = st.selectbox('x-axis data', ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata'], index=0)

# Create a dropdown Select widget for the y data: y_select
y_select = st.selectbox('y-axis data', ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata'], index=1)


# Create the layout
update_plot()
# Display the layout using Streamlit
st.bokeh_chart(plot)

# Load Indonesian province GeoJSON data
gdf = gpd.read_file("https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.geojson")

# Rename for consistency
gdf = gdf.rename(columns={'propinsi': 'Provinsi'})

# Merge your data with geospatial shapes
data_2020 = data.loc[2020].reset_index()
gdf = gdf.merge(data_2020, on='Provinsi', how='inner')

# Extract polygon coordinates
gdf['x'] = gdf.geometry.apply(lambda poly: [list(p.exterior.coords.xy[0]) for p in poly.geoms] if poly.geom_type == 'MultiPolygon' else [poly.exterior.coords.xy[0]])
gdf['y'] = gdf.geometry.apply(lambda poly: [list(p.exterior.coords.xy[1]) for p in poly.geoms] if poly.geom_type == 'MultiPolygon' else [poly.exterior.coords.xy[1]])

# Create ColumnDataSource
geo_source = ColumnDataSource(gdf)

# Create a Bokeh plot
geo_plot = figure(
    title='Peta Produksi Padi per Provinsi (2020)',
    x_axis_label='Longitude',
    y_axis_label='Latitude',
    plot_width=700,
    plot_height=500,
    tools='pan,wheel_zoom,reset,hover',
    tooltips=[("Provinsi", "@Provinsi"), ("Produksi", "@Produksi")]
)

# Draw the provinces
geo_plot.patches('x', 'y', source=geo_source, fill_alpha=0.7, fill_color='lightgreen', line_color='black', line_width=0.5)

# Display it in Streamlit
st.subheader("Peta Geospasial - Data Tahun 2020")
st.bokeh_chart(geo_plot)