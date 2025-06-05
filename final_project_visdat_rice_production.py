import streamlit as st
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.embed import components

# Load your data (replace this with your actual data loading)
data = pd.read_csv("https://github.com/sawsannn/Data-Visualization-of-Indonesia-Rice-Production/blob/main/Data_Tanaman_Padi_Sumatera_version_1.csv?raw=true")  # or your DataFrame

# Streamlit sidebar widgets
selected_year = st.sidebar.slider("Select Year", int(data['Tahun'].min()), int(data['Tahun'].max()), int(data['Tahun'].min()))
selected_province = st.sidebar.selectbox("Select Province", data['Provinsi'].unique())

# Filter data for scatter plot
scatter_data = data[data['Tahun'] == selected_year]

# Scatter plot: Luas Panen vs Produksi for selected year
source_scatter = ColumnDataSource(scatter_data)

scatter_plot = figure(title=f"Scatter Plot for Year {selected_year}",
                      x_axis_label="Luas Panen",
                      y_axis_label="Produksi",
                      tools="pan,wheel_zoom,box_zoom,reset,hover")

scatter_plot.circle('Luas Panen', 'Produksi', source=source_scatter, size=7, color='navy', alpha=0.6)

hover = scatter_plot.select_one(HoverTool)
hover.tooltips = [("Provinsi", "@Provinsi"), ("Produksi", "@Produksi"), ("Luas Panen", "@{Luas Panen}")]

# Filter data for line plot
line_data = data[data['Provinsi'] == selected_province].sort_values('Tahun')
source_line = ColumnDataSource(line_data)

# Line plot: Produksi over years for selected province
line_plot = figure(title=f"Produksi Over Time - {selected_province}",
                   x_axis_label="Year",
                   y_axis_label="Produksi",
                   x_range=(data['Tahun'].min(), data['Tahun'].max()),
                   tools="pan,wheel_zoom,box_zoom,reset,hover")

line_plot.line('Tahun', 'Produksi', source=source_line, line_width=2, color='green')
line_plot.circle('Tahun', 'Produksi', source=source_line, size=7, color='green', alpha=0.6)

hover_line = line_plot.select_one(HoverTool)
hover_line.tooltips = [("Year", "@Tahun"), ("Produksi", "@Produksi")]

# Embed Bokeh plots in Streamlit
from bokeh.embed import components

scatter_script, scatter_div = components(scatter_plot)
line_script, line_div = components(line_plot)

st.markdown("### Scatter Plot")
st.components.v1.html(scatter_div + scatter_script, height=400)

st.markdown("### Line Plot")
st.components.v1.html(line_div + line_script, height=400)
