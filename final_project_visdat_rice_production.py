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

st.title("Indonesia Rice Production - Interactive Line Plot")

# Dropdown to select province
province = st.selectbox("Select Province:", prov_list)

# Filter data for chosen province & reset index so 'Tahun' is column
df_prov = data[data['Provinsi'] == province].reset_index()

# Prepare data for Bokeh
source = ColumnDataSource(df_prov)

# Create Bokeh figure
p = figure(
    title=f"Yearly Trends for {province}",
    x_axis_label='Year',
    y_axis_label='Value',
    plot_width=800,
    plot_height=500,
    tools="pan,wheel_zoom,reset,save"  # Removed box_zoom
)

# Add hover tool with all variables
tooltips = [("Year", "@Tahun")]
tooltips += [(var, f"@{{{var}}}") for var in variables]
hover = HoverTool(tooltips=tooltips)
p.add_tools(hover)

# Plot a line and circle for each variable
for i, var in enumerate(variables):
    p.line('Tahun', var, source=source, line_width=2, color=colors[i], legend_label=var)
    p.circle('Tahun', var, source=source, fill_color="white", size=6, color=colors[i])

p.legend.location = "top_left"
p.legend.click_policy = "hide"

# Display plot in Streamlit using streamlit_bokeh
streamlit_bokeh(p, use_container_width=True)
