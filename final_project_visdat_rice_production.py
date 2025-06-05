import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Category10, Category20
from bokeh.models import NumeralTickFormatter
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

# Variables for dropdown
variables = ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata']

# Provinces list for lines
prov_list = data['Provinsi'].unique().tolist()

st.title("Indonesia Rice Production - Province Trends by Variable")

# Dropdown to select one variable to plot
selected_var = st.selectbox("Select Variable:", variables)

# Choose a palette big enough for provinces
palette = Category20[20] if len(prov_list) <= 20 else Category10[10]

# Create figure
p = figure(
    title=f"{selected_var} Trends for all Provinces",
    x_axis_label='Year',
    y_axis_label=selected_var,
    width=900,
    height=500,
    tools="pan,wheel_zoom,reset,save"
)

# Format y-axis numbers with commas
p.yaxis.formatter = NumeralTickFormatter(format="0,0")

# Add hover tool
hover = HoverTool(tooltips=[("Year", "@x"), ("Province", "@provinsi"), (selected_var, "@y")])
p.add_tools(hover)

# Plot each province's line
for i, prov in enumerate(prov_list):
    df_prov = data[data['Provinsi'] == prov].reset_index()
    source = ColumnDataSource(data={
        'x': df_prov['Tahun'],
        'y': df_prov[selected_var],
        'provinsi': [prov] * len(df_prov)
    })
    color = palette[i % len(palette)]
    p.line('x', 'y', source=source, line_width=2, color=color, legend_label=prov)
    p.circle('x', 'y', source=source, size=6, color=color, fill_color="white")

p.legend.location = "top_left"
p.legend.click_policy = "hide"

# Display plot
streamlit_bokeh(p, use_container_width=True)
