import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Category10, Category20
from bokeh.models import NumeralTickFormatter
from bokeh.transform import factor_cmap
from streamlit_bokeh import streamlit_bokeh

data = pd.read_csv(
    'https://github.com/sawsannn/Data-Visualization-of-Indonesia-Rice-Production/blob/main/Data_Tanaman_Padi_Sumatera_version_1.csv?raw=true'
)
data.set_index('Tahun', inplace=True)

# Variables
variables = ['Produksi', 'Luas Panen', 'Curah hujan', 'Kelembapan', 'Suhu rata-rata']

# Province list
prov_list = data['Provinsi'].unique().tolist()
palette = Category20[20] if len(prov_list) <= 20 else Category10[10]

st.title("Sumatera Island Rice Production Visualization")

tab1, tab2, tab3 = st.tabs(["All Provinces by Feature", "Single Province by Feature", "Top 5 Provinces with Highest Rice Production by Year"])

with tab1:
    st.header("Trend of A Feature")
    st.write("Select one feature to see the trend from 1993 to 2020")
    selected_var = st.selectbox("Select Feature:", variables, key="tab1_var")

    p1 = figure(
        title=f"{selected_var} Trends for All Provinces",
        x_axis_label='Year',
        y_axis_label=selected_var,
        width=800,
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
    st.header("Trend of A Feature and Province")
    st.write("Select one feature and one province to see the trend from 1993 to 2020")
    province = st.selectbox("Select Province:", prov_list, key="tab2_prov")
    selected_var_single = st.selectbox("Select Feature:", variables, key="tab2_var")

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

with tab3:
    st.header("Top 5 Provinces with Highest Rice Production Each Year")

    # Year slider 
    year_min = int(data.index.min())
    year_max = int(data.index.max())
    selected_year = st.slider("Select Year:", min_value=year_min, max_value=year_max, value=year_min, key="top5_year")

    # Filter and get top 5 provinces by production for selected year
    df_year = data.loc[selected_year].reset_index() if selected_year in data.index else pd.DataFrame()
    df_top5 = df_year.nlargest(5, 'Produksi') if not df_year.empty else pd.DataFrame()

    if df_top5.empty:
        st.warning("No data available for selected year.")
    else:
        source_top5 = ColumnDataSource(df_top5)
        provinces_top5 = df_top5['Provinsi'].tolist()
        colors_top5 = Category10[5]

        p3 = figure(
            y_range=provinces_top5[::-1], 
            x_axis_label='Produksi',
            title=f"Top 5 Rice Production Provinces in {selected_year}",
            height=400,
            width=700,
            tools="pan,wheel_zoom,reset,save"
        )

        p3.hbar(
            y='Provinsi',
            right='Produksi',
            height=0.6,
            color=factor_cmap('Provinsi', palette=colors_top5, factors=provinces_top5),
            source=source_top5
        )

        hover3 = HoverTool()
        hover3.tooltips = [
            ("Province", "@Provinsi"),
            ("Production", "@Produksi{0,0}"),
            ("Year", str(selected_year))
        ]
        p3.add_tools(hover3)

        p3.xaxis.formatter = NumeralTickFormatter(format="0,0")
        p3.ygrid.grid_line_color = None

        streamlit_bokeh(p3, use_container_width=True, key="top5_plot")
