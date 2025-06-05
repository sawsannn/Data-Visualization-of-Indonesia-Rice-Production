import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Category10
from streamlit_bokeh import streamlit_bokeh

# Load data and set index
data = pd.read_csv(
    'https://github.com/sawsannn/Data-Visualization-of-Indonesia-Rice-Production/blob/main/Data_Tanaman_Padi_Sumatera_version_1.csv?raw=true'
)
data.set_index('Tahun', inplace=True)

# Rename columns for easier use
data.rename(columns={
    'Suhu rata-rata': 'suhu_rata',
    'Curah hujan': 'curah_hujan',
    'Luas Panen': 'luas_panen'
}, inplace=True)

# Variables to plot
variables = ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata']
colors = Category10[len(variables)]

# Province list for dropdown
prov_list = data['Provinsi'].unique().tolist()

st.title("Indonesia Rice Production - Line Plot")

# Dropdown to select province
province = st.selectbox("Select Province:", prov_list)

# Dropdown to select variable (only one line shown)
selected_var = st.selectbox("Select Variable to Plot:", variables)

# Filter data for chosen province & reset index so 'Tahun' is column
df_prov = data[data['Provinsi'] == province].reset_index()

# Prepare data for Bokeh
source = ColumnDataSource(df_prov)

# Create Bokeh figure
p = figure(
    title=f"{selected_var} Trend for {province}",
    x_axis_label='Year',
    y_axis_label=selected_var,
    width=800,
    height=500,
    tools="pan,wheel_zoom,reset,save"
)

# Add hover tool
hover = HoverTool(tooltips=[
    ("Year", "@Tahun"),
    (selected_var, f"@{{{selected_var}}}")
])
p.add_tools(hover)

# Get color for selected variable
color = colors[variables.index(selected_var)]

# Plot single line and circles for selected variable
p.line('Tahun', selected_var, source=source, line_width=3, color=color, legend_label=selected_var)
p.circle('Tahun', selected_var, source=source, size=8, fill_color="white", color=color)

p.legend.location = "top_left"
p.legend.click_policy = "hide"

# Display plot in Streamlit using streamlit_bokeh
streamlit_bokeh(p, use_container_width=True)
