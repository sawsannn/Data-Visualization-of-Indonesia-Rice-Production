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

# Rename columns for consistency (optional)
data.rename(columns={
    'Suhu rata-rata': 'suhu_rata',
    'Curah hujan': 'curah_hujan',
    'Luas Panen': 'luas_panen'
}, inplace=True)

# Variables (using original names for display, but you can change)
variables = ['Produksi', 'luas_panen', 'curah_hujan', 'Kelembapan', 'suhu_rata']

# Province list
prov_list = data['Provinsi'].unique().tolist()

# Choose palette large enough for provinces
palette = Category20[20] if len(prov_list) <= 20 else Category10[10]

st.title("Indonesia Rice Production Visualization")

# Create tabs
tab1, tab2 = st.tabs(["All Provinces by Variable", "Single Province by Variable"])

with tab1:
    st.header("All Provinces: Select Variable to Plot")
    selected_var = st.selectbox("Select Variable:", variables, key="tab1_var")

    p1 = figure(
        title=f"{selected_var} Trends for All Provinces",
        x_axis_label='Year',
        y_axis_label=selected_var,
        width=900,
        height=500,
        tools="pan,wheel_zoom,reset,save"
    )
    p1.yaxis.formatter = NumeralTickFormatter(format="0,0")
    hover1 = HoverTool(tooltips=[("Year", "@x"), ("Province", "@provinsi"), (selected_var, "@y")])
    p1.add_tools(hover1)

    for i, prov in enumerate(prov_list):
        df_prov = data[data['Provinsi'] == prov].reset_index()
        source = ColumnDataSource(data={
            'x': df_prov['Tahun'],
            'y': df_prov[selected_var],
            'provinsi': [prov]*len(df_prov)
        })
        color = palette[i % len(palette)]
        p1.line('x', 'y', source=source, line_width=2, color=color, legend_label=prov)
        p1.circle('x', 'y', source=source, size=6, color=color, fill_color="white")

    p1.legend.location = "top_left"
    p1.legend.click_policy = "hide"

    streamlit_bokeh(p1, use_container_width=True, key="all_provs_plot")

with tab2:
    st.header("Single Province: Select Province and Variable")
    province = st.selectbox("Select Province:", prov_list, key="tab2_prov")
    selected_var_single = st.selectbox("Select Variable:", variables, key="tab2_var")

    df_prov_single = data[data['Provinsi'] == province].reset_index()
    source_single = ColumnDataSource(df_prov_single)

    p2 = figure(
        title=f"{selected_var_single} Trend for {province}",
        x_axis_label='Year',
        y_axis_label=selected_var_single,
        width=800,
        height=500,
        tools="pan,wheel_zoom,reset,save"
    )
    p2.yaxis.formatter = NumeralTickFormatter(format="0,0")

    hover2 = HoverTool(tooltips=[("Year", "@Tahun"), (selected_var_single, f"@{{{selected_var_single}}}")])
    p2.add_tools(hover2)

    color_single = Category10[len(variables)][variables.index(selected_var_single)]

    p2.line('Tahun', selected_var_single, source=source_single, line_width=3, color=color_single, legend_label=selected_var_single)
    p2.circle('Tahun', selected_var_single, source=source_single, size=8, fill_color="white", color=color_single)

    p2.legend.location = "top_left"
    p2.legend.click_policy = "hide"

    streamlit_bokeh(p2, use_container_width=True, key="single_prov_plot")
