import streamlit as st
import plotly.express as px

st.set_page_config(page_title="About materials", page_icon="🌍")

st.title('Materials')


# treemap chart

import landscape_materials as ls
materials = ls.parse_materials()
st.write(materials)
scatter_fig = px.treemap(materials,path=[px.Constant('Materials'),'M1', 'M2','M3'], color='Embodied-CO2eq', hover_data=['Embodied-CO2eq'],
                  color_continuous_scale='RdBu_r')
st.plotly_chart(scatter_fig)
