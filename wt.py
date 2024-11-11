import streamlit as st
st.set_page_config(layout="wide")
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.stats import beta, norm, uniform
import matplotlib.pyplot as plt

title_col, space_col, logo_col = st.columns([4,1,1])

with title_col:
    st.write("""
            # War Thunder Data Science App :boom:
            **Bayesian A/B Testing, K-Means Clustering, Linear Regression, and Statistical Techniques Applied to War Thunder Data**
            """)
    st.write('Developed by **A.C. Sanders** - also known in the War Thunder community as *DrKnoway*')

with space_col:
    st.empty() # used for padding

with logo_col:
    # st.empty()  # Create an empty space to help formmat the image location
    st.image("knoway_eye.png",
              width=200,
              )

# header for the section that generates line charts for vehicle performance over time
st.header("Vehicle Trends")

# Load and cache the DataFrame
@st.cache_data  # You can upgrade Streamlit to use @st.cache_data for newer versions
def load_data():
    return pd.read_csv("full_data.csv") # full_data is available in my Github repo

# Load the data
data = load_data()

# Make a copy of the DataFrame
df_copy = data.copy()

# Ensure 'date' column is in datetime format
df_copy['date'] = pd.to_datetime(df_copy['date'])

# Create columns for the dropdown menus
col1, col2, col3, col4 = st.columns(4)

# 1st dropdown menu for the type of vehicle - default set to ground vehicles
with col1:
    vehicle_types = df_copy['cls'].unique()
    # Set default to "Ground" if it exists in vehicle_types
    default_vehicle_type = "Ground_vehicles" if "Ground_vehicles" in vehicle_types else vehicle_types[0]
    selected_vehicle_types = st.selectbox("Vehicle Type", vehicle_types, index=list(vehicle_types).index(default_vehicle_type))

# Filter df_copy based on the selected vehicle type (cls in the dataset)
filtered_by_type_df = df_copy[df_copy['cls'] == selected_vehicle_types]

# 2nd dropdown for selecting nation
with col2:
    nations = filtered_by_type_df['nation'].unique()
    # Set default to "Germany" if it exists in nations
    default_nation = ["USA"] if "USA" in nations else [nations[0]]
    selected_nations = st.multiselect("Nation", nations, default=default_nation)

# Filter based on selected nation
filtered_by_nation_df = filtered_by_type_df[filtered_by_type_df['nation'].isin(selected_nations)]

# 3rd dropdown for BR (i.e., battle rating in the game)
with col3:
    br_values = filtered_by_nation_df['rb_br'].unique()
    # Set default to 1.0 if it exists in br_values
    default_br = [1.0] if 1.0 in br_values else [sorted(br_values)[0]]
    selected_br = st.multiselect("BR", sorted(br_values, reverse=True), default=default_br)

# Filter based on selected BR
filtered_by_br_df = filtered_by_nation_df[filtered_by_nation_df['rb_br'].isin(selected_br)]

# 4th dropdown for the metric to analyze/visualize
with col4:
    metrics = [ 
        'rb_ground_frags_per_death', 
        'rb_ground_frags_per_battle',
        'rb_win_rate',
        'rb_battles',  
        'rb_air_frags_per_death', 
        'rb_air_frags_per_battle' 
    ]
    selected_metric = st.selectbox("Metric", metrics, index=0)  # Defaults to the first metric

# 5th dropdown for Vehicle Name - filtered based on type and nation selected
vehicle_names = filtered_by_br_df['name'].unique()
selected_vehicle_names = st.multiselect("Vehicle Name", vehicle_names, default=list(vehicle_names) if vehicle_names.size > 0 else [])

# Filter the df_copy dataframe based on user selections from the dropdown menus
final_filtered_df = df_copy[
    (df_copy['cls'] == selected_vehicle_types) &
    (df_copy['nation'].isin(selected_nations)) &
    (df_copy['rb_br'].isin(selected_br)) &
    (df_copy['name'].isin(selected_vehicle_names))
]

# Sort by date and get unique dates - ensure formatted dates using dt.strftime()
unique_dates = sorted(df_copy['date'].dt.strftime('%m/%d/%y').unique())

# Add the date range select slider
date_range = st.select_slider(
    "Select date range:",
    options=unique_dates,
    value=(unique_dates[0], unique_dates[-1]),
    key='date_range_slider'
)

# Convert selected start and end dates back to datetime for filtering
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

# Filter based on the date range selected
final_filtered_df = final_filtered_df[
    (final_filtered_df['date'] >= start_date) & 
    (final_filtered_df['date'] <= end_date)
]


# show row count in the filtered DataFrame - used for debugging - un-comment if needed
# st.write(f"Filtered DataFrame rows: {final_filtered_df.shape[0]}") 

# plot the rows if there is data
if final_filtered_df.shape[0] > 0:
 # Create boxplot
    fig_box = px.box(final_filtered_df, 
                     x='name',  # Categories (vehicles)
                     y=selected_metric,  # Metric
                     color='name',  # This will color the boxes by vehicle name
                     title=f"<b>Distribution of {selected_metric} by Vehicle</b>",
                     labels={'name': 'Vehicle Name', selected_metric: selected_metric})
    
    fig_box.update_layout(template='plotly')

    fig_box.update_layout(title=dict(font=dict(size=24)), 
                          xaxis_title=dict(font=dict(size=18)), 
                          yaxis_title=dict(font=dict(size=18)),
                          width=900,
                          height=600)

    # Create line plot
    fig = px.line(final_filtered_df, 
                  x='date', 
                  y=selected_metric, 
                  color='name',  # this will create separate lines for each vehicle
                  title=f"<b>Performance Over Time</b><br><span style='font-size:16px;'>Selected Metric: {selected_metric}</span>",
                  labels={'date': 'Date', selected_metric: selected_metric}, 
                  hover_data=['name', 'nation', 'rb_br'])
    
    fig.update_layout(template='plotly')

    fig.update_traces(line=dict(width=2), mode='lines+markers')  
    fig.update_layout(title=dict(font=dict(size=24)), 
                        xaxis_title=dict(font=dict(size=18)), 
                        yaxis_title=dict(font=dict(size=18)),
                        width = 900,
                        height = 600) 

    # Show the plot and fill the container width (use_container_width = True) -- stylistic/helps format the plot on the screen
    st.plotly_chart(fig, use_container_width=True) 

    # Show the boxplot
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.write("No data available") # display this message if the selections and resulting dataframe lack any data

####################################################################################################################################

# Heatmap of Aggregated Win Rates

####################################################################################################################################

st.subheader("Aggregated Win Rates by Nation")

# copy of our data
wr_df = data.copy()

# convert date column in datetime format
wr_df['date'] = pd.to_datetime(wr_df['date'])

# Get unique vehicle types from the 'cls' column
vehicle_types = wr_df['cls'].unique()

# get rid of "Fleet" from vehicle_types in selection
filtered_vehicle_types_heatmap = [vt for vt in vehicle_types if vt != "Fleet"]

# dropdown menu to select the vehicle type
default_index_heatmap = filtered_vehicle_types_heatmap.index("Ground_vehicles") if "Ground_vehicles" in filtered_vehicle_types_heatmap else 0
selected_vehicle_type = st.selectbox(
    "Select Vehicle Type:",
    options=filtered_vehicle_types_heatmap,
    index=default_index_heatmap  # default to "Ground_vehicles" otherwise the first type
)

# Sort by date and get unique dates - make sure it is formatted correctly (MM/DD/YY)
unique_dates = sorted(wr_df['date'].dt.strftime('%m/%d/%y').unique())

# date range slider - additional filtering by date
date_range = st.select_slider(
    "Select date range:",
    options=unique_dates,
    value=(unique_dates[0], unique_dates[-1])
)

# convert start and end dates back to datetime for filtering
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

# Filter for selected type and date
filtered_df = wr_df[
    (wr_df['cls'] == selected_vehicle_type) &
    (wr_df['date'] >= start_date) & 
    (wr_df['date'] <= end_date)
]

# make a br_range variable - this will be a more generic/broad category
filtered_df['br_range'] = np.floor(filtered_df['rb_br']).astype(int) # e.g., 1.0, 1.3, and 1.7 will all be 1 for br_range (a broad category)
agg_wr_df = filtered_df.groupby(['nation', 'br_range']).rb_win_rate.mean().reset_index()
agg_wr_pivot = agg_wr_df.pivot(index='nation', columns='br_range', values='rb_win_rate')

# create heatmap
fig_wr_heatmap = px.imshow(
    agg_wr_pivot,
    color_continuous_scale='RdBu',
    labels=dict(x='BR Range', y='Nation', color='rb_win_rate')
)

# let us show all x-axis ticks
fig_wr_heatmap.update_xaxes(tickmode='linear')

fig_wr_heatmap.update_traces(
    text=agg_wr_pivot.round(1).astype(str),  # round values to 1 decimal and convert to string
    texttemplate="%{text}",  # rounded values as text
    textfont=dict(size=10),  # font size
    hoverinfo='text'  # hover info - show the values
)

# layout updates and styling
fig_wr_heatmap.update_layout(
    template='plotly',
    width=900,   
    height=700   
)

# Show heatmap with customized dimensions
st.plotly_chart(fig_wr_heatmap, use_container_width=True)


#######################################################################################################################

# k-means clustering

#######################################################################################################################

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
from datetime import datetime, timedelta

st.header('k-Means Clustering')
st.subheader('Ranked Ground Vehicle Performance Groups')
st.write("""k-Means clustering is performed on several engagement variables like *K/D*
            and *vehicles destroyed per battle*. The algorithm clusters vehicles into one
            of three groups: **high performers**, **moderate performers**, and **low performers**.
            After clustering, an interactive scatterplot is generated showing displaying each cluster of vehicles for the variables
            K/D and Frags per Battle. The full results can be downloaded as a CSV file.""")

# Scatter plot function
def plot_scatter_plot(df, x_metric, y_metric, color_metric):
    fig = px.scatter(
        df,
        x=x_metric,
        y=y_metric,
        color=color_metric,
        hover_data=['name', 'cls', 'nation'],
        # add OLS regression line
        trendline = "ols",
        # apply it to the overall dataset and not the segments
        trendline_scope = "overall",
        title="<b>Scatter Plot of K/D vs Frags per Battle Colored by Performance Cluster</b>"
    )
    
    fig.update_layout(
        title=dict(font=dict(size=20)),
        xaxis_title=x_metric,
        yaxis_title=y_metric,
        legend_title=dict(text=color_metric, font=dict(size=14)),
        xaxis=dict(title_font=dict(size=16)),
        yaxis=dict(title_font=dict(size=16)),
        width=900,
        height=600
    )
    
    # markers
    fig.update_traces(marker=dict(size=8))
    
    return fig

# Clustering metrics
key_metrics = ['rb_ground_frags_per_death', 'rb_ground_frags_per_battle']

# Processing function with caching
@st.cache_data
def filter_and_segment_data(df, key_metrics):
    recent_date = datetime.now() - timedelta(days=30)
    # Filter data for the last 30 days and drop rows with NaN in key metrics
    filtered_df = df[df['date'] >= recent_date].dropna(subset=key_metrics)
    filtered_df = filtered_df[~filtered_df['cls'].isin(['Fleet', 'Aviation'])]
    filtered_df['br_range'] = np.floor(filtered_df['rb_br']).astype(int)
    
    # Group by vehicle and aggregate key metrics
    aggregated_df = filtered_df.groupby('name', as_index=False).agg({
        'rb_ground_frags_per_death': 'mean',
        'rb_ground_frags_per_battle': 'mean',
        'rb_win_rate': 'mean',
        'br_range': 'first',
        'cls': 'first',
        'nation': 'first'
    })
    
    return aggregated_df

# Perform k-means clustering only on the selected BR range
def perform_kmeans_and_label(data, key_metrics):
    scaler = StandardScaler() 
    standardized_metrics = scaler.fit_transform(data[key_metrics])
    kmeans = KMeans(n_clusters=3, random_state=42)
    data['cluster'] = kmeans.fit_predict(standardized_metrics)
    
    # Centroid calculation
    centroids = kmeans.cluster_centers_
    centroids_original_scale = scaler.inverse_transform(centroids)
    avg_centroids = np.mean(centroids_original_scale, axis=1)
    
    # Label mapping
    label_map = {i: 'high performance' if avg_centroids[i] == max(avg_centroids)
                 else 'low performance' if avg_centroids[i] == min(avg_centroids)
                 else 'moderate performance' for i in range(3)}
    
    data['performance_label'] = data['cluster'].map(label_map)
    
    return data

# Ensure 'date' column is in datetime format
df_copy['date'] = pd.to_datetime(df_copy['date'])

# Filter and segment data once, caching the result
aggregated_df = filter_and_segment_data(df_copy, key_metrics)

# User input: select BR range
selected_br = st.selectbox("Select a BR range for clustering results", list(range(1, 14)))

# Filter data for the selected BR range
selected_br_data = aggregated_df[aggregated_df['br_range'] == selected_br]

if not selected_br_data.empty:
    # Perform k-means clustering only for the selected BR data
    clustering_results = perform_kmeans_and_label(selected_br_data, key_metrics)
    
    # Show the data and plot scatter plot
    st.dataframe(clustering_results)
    st.write(f"Clustering completed for BR {selected_br}.")

    st.header("Linear Regression Applied to K-Means Cluster Results")
    st.write(f"Dependent variable (y) = K/D")
    st.write(f"Independent variable (x) = Frags per Battle")

    fig = plot_scatter_plot(
        clustering_results,
        x_metric='rb_ground_frags_per_battle',
        y_metric='rb_ground_frags_per_death',
        color_metric='performance_label'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write(f"No data available for BR {selected_br}.")

# get regression info

trendline_results = px.get_trendline_results(fig)
if not trendline_results.empty:
    model_summary = trendline_results.iloc[0]["px_fit_results"].summary()

    # Display regression summary
    st.subheader(f"Linear Regression Summary for BR {selected_br}")
    st.code(model_summary.as_text(), language="text")
    # st.text(model_summary) 

    # convert to a table
    # st.write("### Coefficients Table")
    # coef_df = pd.DataFrame(model_summary.tables[1].data[1:], columns=model_summary.tables[1].data[0])
    # st.dataframe(coef_df)

####################################################################################################################

# Bayesian Statistics

####################################################################################################################

st.header("Bayesian A/B Testing")
st.subheader("Calculate the Probability that One Nation (A) Has a Better Win Rate than Another Nation (B)")
st.write("""This tool tests the win rates between two nations at a specified BR range using Bayesian statistical methods. 
            Historical data from the last 60 days is used in conjunction with non-informative priors. *Monte Carlo* simulation 
            is employed to create the posterior distributions for *win rates*, and the *probability* that the first selected nation's win rate is **better**
            than the second nation's win rate is computed. Additionally, the distribution of differences between the win rates are plotted along with 
            a *95% credibility interval*. 
            """)
st.write("**Please select two nations to run a Bayesian statistical analysis on *win rates***")

# function to run Bayesian testing on numeric or continuous data
# I originally developed this for test and control groups for A/B experiments and I've retained some of these names for variables
def bayesian_ab_test_numeric(nation_one_series, nation_two_series, nation_one, nation_two, n_simulations=10000):
    # calculate sample statistics - we need these for posteriors
    test_mean, test_std = np.mean(nation_one_series), np.std(nation_one_series, ddof=1)
    control_mean, control_std = np.mean(nation_two_series), np.std(nation_two_series, ddof=1)
    test_n, control_n = len(nation_one_series), len(nation_two_series)
    
    # Priors - set these to be non-informmative gaussian priors
    mu0, s0, n0 = 0, 1, 0
    
    # posterior parameters needed for Monte Carlo simulation - non-informative priors lets the data speak for itself
    inv_vars_test = (n0 / s0**2, test_n / test_std**2)
    posterior_mean_test = np.average((mu0, test_mean), weights=inv_vars_test)
    posterior_std_test = 1 / np.sqrt(np.sum(inv_vars_test))
    
    inv_vars_control = (n0 / s0**2, control_n / control_std**2)
    posterior_mean_control = np.average((mu0, control_mean), weights=inv_vars_control)
    posterior_std_control = 1 / np.sqrt(np.sum(inv_vars_control))
    
    # Monte Carlo sampling time -- use 10,000 simulations
    test_samples = norm.rvs(loc=posterior_mean_test, scale=posterior_std_test, size=n_simulations)
    control_samples = norm.rvs(loc=posterior_mean_control, scale=posterior_std_control, size=n_simulations)
    
    # Probability that vehicle one beats vehicle two
    prob_vehicle_one_beats_vehicle_two = round(np.mean(test_samples > control_samples), 2) * 100
    
    # Credible Interval for the difference - using 95% credibile interval
    diff_samples = test_samples - control_samples
    credible_interval = np.percentile(diff_samples, [2.5, 97.5])
    
    # results - probability that A is better than B
    st.markdown(
    f"""Probability that the **{nation_one}** has a better win rate than **{nation_two}** = 
    <span style='color: green; font-weight:bold;'>{prob_vehicle_one_beats_vehicle_two}%</span>""",
    unsafe_allow_html=True
    )

    # credibility interval
    st.write(f"95% Credibility Interval for difference: [{round(credible_interval[0],1)}, {round(credible_interval[1],1)}]")
    
    return test_samples, control_samples, diff_samples, credible_interval


# Plotting function for posterior distributions
def create_posterior_plots(test_samples, control_samples, vehicle_one_name, vehicle_two_name, test_mean, control_mean):
    # make histograms or distplots to visualize the distributions of the posterior samples
    fig_a = ff.create_distplot([test_samples, control_samples], 
                               group_labels=[vehicle_one_name, vehicle_two_name], 
                               )
    fig_a.update_traces(nbinsx = 100, autobinx = True, selector = {'type':'histogram'})
    fig_a.add_vline(x=test_samples.mean(), line_width = 3, line_dash='dash', line_color= 'hotpink', annotation_text = f'mean <br> {round(test_mean,1)}', annotation_position = 'bottom')
    fig_a.add_vline(x=control_samples.mean(), line_width = 3, line_dash='dash', line_color= 'purple', annotation_text = f'mean <br> {round(control_mean,1)}', annotation_position = 'bottom')
    fig_a.update_layout(# title_text = 'Posterior Distributions of Selected Vehicle K/D Ratios',
                        # title_font=dict(size=24, family="Inter Bold"), # I think Streamlit uses Inter font family
                        autosize = True,
                        height = 700)
    
    # show
    st.plotly_chart(fig_a, use_container_width=True)

# Plotting function for difference distribution - 
def create_difference_plot(diff_samples, credible_interval, vehicle_one_name, vehicle_two_name):
    # round the credible interval and median to 1 decimal
    credible_interval_rounded = [round(val, 1) for val in credible_interval]
    diff_samples_median = round(np.median(diff_samples), 1)

    # create plot
    fig2b = ff.create_distplot([diff_samples], 
                               group_labels=[f"{vehicle_one_name} - {vehicle_two_name}"], 
                               colors = ['aquamarine'],
    )

    fig2b.update_traces(nbinsx = 100, autobinx=True, selector = {'type':'histogram'})

    # Add vertical lines for credibility interval, 0 difference, and median (the median is the most likely lift)
    fig2b.add_vline(x=credible_interval_rounded[0], line_width=3, line_dash='dash', line_color='red', 
                    annotation_text=f'95% Lower Bound <br>{credible_interval_rounded[0]}', annotation_position='top')
    fig2b.add_vline(x=credible_interval_rounded[1], line_width=3, line_dash='dash', line_color='red', 
                    annotation_text=f'95% Upper Bound <br>{credible_interval_rounded[1]}', annotation_position='top')
    fig2b.add_vline(x=diff_samples_median, line_width=3, line_color='dodgerblue', 
                    annotation_text=f'Median <br>{diff_samples_median}', annotation_position='bottom')
    fig2b.add_vline(x=0, line_width=3, line_dash='dot', line_color='orange', 
                    annotation_text='0', annotation_position='bottom')

    fig2b.update_layout(
        # title_text=f"Distribution of Differences in K/D for 10,000 Simulations: {vehicle_one_name} K/D Minus {vehicle_two_name} K/D",
        # title_font=dict(size=24, family="Inter Bold"),
        height = 700,
        autosize=True
    )

    # show plot
    st.plotly_chart(fig2b, use_container_width=True)


# User inputs, filtering, and running the Bayesian test

df_bayes = data.copy()

# Filter for ground vehicles only and remove nulls in 'rb_win_rate'
df_bayes_filtered = df_bayes[(df_bayes['cls'] == 'Ground_vehicles') & df_bayes['rb_win_rate'].notna()]

# Convert to datetime and filter for the last 60 days
df_bayes_filtered['date'] = pd.to_datetime(df_bayes_filtered['date'], errors='coerce')
sixty_days_ago = datetime.now() - timedelta(days=60)
df_bayes_filtered = df_bayes_filtered[df_bayes_filtered['date'] >= sixty_days_ago]

# Create 'br_range' variable for broad BR categories
df_bayes_filtered['br_range'] = np.floor(df_bayes_filtered['rb_br']).astype(int)

# User input for BR range
selected_br_range = st.selectbox("Select BR Range:", sorted(df_bayes_filtered['br_range'].unique()))
df_bayes_filtered = df_bayes_filtered[df_bayes_filtered['br_range'] == selected_br_range]

# Columns for selecting two nations
col1, col2 = st.columns(2)

# First nation selection
with col1:
    st.subheader("Nation One Selection")
    nation_one = st.selectbox("Select Nation for First Group:", sorted(df_bayes_filtered['nation'].unique()))
    if nation_one:
        nation_one_series = df_bayes_filtered[df_bayes_filtered['nation'] == nation_one]['rb_win_rate']

# Second nation selection
with col2:
    st.subheader("Nation Two Selection")
    nation_two = st.selectbox("Select Nation for Second Group:", sorted(df_bayes_filtered['nation'].unique()), key="nation_two")
    if nation_two:
        nation_two_series = df_bayes_filtered[df_bayes_filtered['nation'] == nation_two]['rb_win_rate']

# Run Bayesian A/B testing if both series are defined
if 'nation_one_series' in locals() and 'nation_two_series' in locals():
    st.write(f"Comparing **{nation_one}** vs **{nation_two}** for BR Range: **{selected_br_range}**")

    # Run Bayesian A/B testing
    test_samples, control_samples, diff_samples, credible_interval = bayesian_ab_test_numeric(
        nation_one_series, nation_two_series, nation_one, nation_two
    )
    
    # Calculate means for posteriors
    test_mean = np.mean(test_samples)
    control_mean = np.mean(control_samples)

    # Display posterior distributions
    st.subheader(f"Posterior Distributions Win Rates for {nation_one} and {nation_two}")
    create_posterior_plots(test_samples, control_samples, nation_one, nation_two, test_mean, control_mean)

    # Display difference distribution plot
    st.subheader("Distribution of Differences in Win Rates")
    st.markdown(f"Difference calculated as **{nation_one}** win rate - **{nation_two}** win rate")
    create_difference_plot(diff_samples, credible_interval, nation_one, nation_two)
else:
    st.write("Please select both nations to run the Bayesian A/B test.")


