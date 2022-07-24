import streamlit as st
import pandas as pd
import plotly.express as px
import utils
import s3fs
import os

# Create connection object.
# `anon=False` means not anonymous, i.e. it uses access keys to pull data.
fs = s3fs.S3FileSystem(anon=False)

# from specklepy.api.client import SpeckleClient
# from specklepy.api.credentials import get_account_from_token

# def read_file(filename):
#     with fs.open(filename) as f:
#         return f
def get_runs():
    """Gets the number of times the iterations have been run
    based on the number of results stored

    Returns:
        int: number of runs in this session
    """
    
    with fs.open('lcawebapp/session/info.txt', 'r') as f:
        s = f.readlines()
        print(s)
        return len(s)

# helper functions to load data
@st.experimental_memo(ttl=600)
def load_csv(iteration):
    with fs.open(f"lcawebapp/session/{iteration}.csv") as f:
    # content = read_file(f"lcawebapp/session/{iteration}.csv")
    # path = f'{SESSION}{iteration}.csv'
        df = pd.read_csv(f, header=0)
    uuids = df.columns
    df.columns = utils.match_id_name(uuids)
    return df

# @st.cache(allow_output_mutation=True)
def load_totals(n_iterations):
    dfs = []
    keys = []
    for i in range(1, n_iterations + 1 , 1):
        df = load_csv(i)
        subtotal = df.sum(axis=1)
        keys.append(str(i))
        dfs.append(subtotal)
    total = pd.concat(dfs, keys = keys).reset_index()
    total.pop('level_1')
    total.columns = ['iteration', 'GWP' ]
    return total

# @st.cache
# def get_latest_stream_commit(speckleServer, speckleToken):
#         # Client
#         client = SpeckleClient(host=speckleServer)  
#         # get account from token
#         account = get_account_from_token(speckleToken, speckleServer)
#         client.authenticate_with_account(account)
#         streams = client.stream.list()
#         stream_names = [s.name for s in streams]
#         s_name = st.selectbox(label="Select stream", options=stream_names)
#         selected_stream = client.stream.search(s_name,limit = 3)[0]
#         # viewer.write(stream)
#         latest_commit = client.commit.list(stream_id=selected_stream.id, limit=1)[0]
#         return selected_stream, latest_commit
    
# Speckle stuff
# def get_embed_view(stream, commit):
#     # <iframe src="https://speckle.xyz/embed?stream=0bacfc3aa6&transparent=true" width="600" height="400" frameborder="0"></iframe>
#     embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + commit.id
#     return st.components.v1.iframe(src=embed_src, height = 400)

# configure page (this must be called before any other Streamlit command)
st.set_page_config(
    page_title="LCA Results",
    page_icon="🌱",
)

# constants
st.write(get_runs())
try:
    max_iteration = get_runs()
    project_area = utils.get_project_area()
except FileNotFoundError:
    st.write('Such empty. Have you run your first simulation?')
else:
    # load data
    total = load_totals(max_iteration)

    # containers
    header = st.container()
    # about_project = st.container()
    # kpis = st.container()
    project_metrics = st.container()
    about_project, kpis = project_metrics.columns(2)
    overview = st.container()
    viewer = st.container()
    iteration_container = st.container()


    with header:
        st.title('LCA Results')
    # about app
    with header.expander("About this dashboard", expanded=False):
        st.markdown("""
        This Dashboard shows the results from the statistical simulations run by the LCA server.
        """
        )
    # sidebar
    with st.sidebar:
        st.title('Snapshots')
        st.write('Select a design snapshopt')
        current_iter = st.slider('Snapshot', 1, max_iteration, max_iteration)  # min: 0h, max: 10, default: 1

    # about project container

    with about_project:
        about_project.subheader('Project metrics')
        # p_metric1, p_metric2 = about_project.columns(2)
        p_metric1 = st.metric('Area', f'{project_area:,.1f} sqm')
        # p_metric1.metric('Total sqm', f'{project_area:,.1f} sqm')
        # total_elements = p_metric2.metric('loading..', 0)
        total_elements = st.metric('loading..', 0)
        

    # initialize three columns for metrics
    with kpis:
        kpis.subheader("KPI's")
        # metric1, metric2, metric3 = st.metric(3)
        metric1 = st.metric('loading...', 0)
        metric2 = st.metric('loading...', 0)
        metric3 = st.metric('loading...', 0)


    # Summary plot

    # add a column converting Kg to Ton in the totals
    total['GWP(Ton CO2eq)'] = total['GWP'].div(1000)
    # plot figure
    with overview:
        st.subheader('Overview:')
        fig = px.box(total, x="iteration", y="GWP(Ton CO2eq)")
        st.plotly_chart(fig, use_container_width= True)

    # with viewer:
    #     viewer.subheader('3D view')
    #     with viewer.expander('Speckle setup', expanded=False):
    #         serverCol, tokenCol = st.columns([1,2])
    #         speckleServer = serverCol.text_input('Server URL', 'speckle.xyz')
    #         speckleToken = tokenCol.text_input("Speckle token", '99a33bf554f23462e45b3095ec002b8eadee863e67')
    #         selected_stream, latest_commit = get_latest_stream_commit(speckleServer, speckleToken)
    #         st.write(latest_commit)
            
    #     get_embed_view(selected_stream, latest_commit)

    with iteration_container:
    # Subheader
        st.subheader(f'Iteration {current_iter}')

        # Create a text element and let know data is loading

        data_load_state = st.text('Loading data...')
        # load data
        data2 = load_csv(current_iter)

    # update total elements
    total_elements.metric('Total elements', len(data2.columns))

    # update loading text element
    data_load_state.text('Loading data...done!')
    # add histogram
    px_histogram = px.histogram(total[total['iteration'] == str(current_iter)]['GWP']/1000, x='GWP')
    st.plotly_chart(px_histogram)

    descriptive = pd.DataFrame.describe(data2)

    # avgGWP = total[total['iteration'] == str(iteration_range)]['GWP'].median()
    # metrics from current run
    avgGWP = descriptive.loc['mean'].sum(axis=0)
    avgStd = descriptive.loc['std'].sum(axis=0)

    # metrics from previous run
    if current_iter == 1:
        prev_GWP = 0
        delta_gwp = None
        prev_std = 0
        delta_std = None
        delta_area = None
    if current_iter != 1 and max_iteration > 1:
        prev_descr = load_csv(current_iter-1).describe()
        prev_GWP = prev_descr.loc['mean'].sum(axis=0)
        delta_gwp= round((avgGWP-prev_GWP)/1000,3)
        prev_std = prev_descr.loc['std'].sum(axis=0)
        delta_std = round((avgStd-prev_std)/1000,3)
        delta_area = round(delta_gwp*1000/project_area,2)

    # KPIS
    with metric1:
        st.metric('Mean GWP', f'{avgGWP/1000:,.2f} Ton COeq', delta = delta_gwp, delta_color='inverse')
    with metric2:
        st.metric('Standard deviation', f'{avgStd/1000:,.2f}', delta=delta_std, delta_color='inverse')
    with metric3:
        st.metric('Mean GWP/Area', f'{avgGWP/project_area:,.2f} KgCO2eq/m2', delta = delta_area, delta_color='inverse')

    # Checkbox to show raw data of iterations
    if st.checkbox(f'Show raw data - Iteration {current_iter}'):
        st.write(data2)

    # show descriptive data for every element # off for now
    # st.write(descriptive)
    col1, col2 = st.columns(2)

    with col1:
        st.write('Mean impact per element')
        bar_chart_mean = px.bar(descriptive.loc['mean'])
        # st.bar_chart(descriptive.loc['mean'], use_container_width=True)
        st.plotly_chart(bar_chart_mean)

    # normalizing by the sum of the impact of each mc trial
    contribution = data2.div(data2.sum(axis=1), axis=0)

    spearman = utils.spearman_corr(data2)
    
    with col2:
        st.write('Correlation to variance')
        
        bar_chart_contr = px.bar(spearman.sort_values(by= 'correlation', ascending=True), x=['correlation', 'pvalue'], orientation='h')

        # st.bar_chart(contribution.mean(axis=0))
        st.plotly_chart(bar_chart_contr)
