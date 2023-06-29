import plotly.graph_objects as go
import plotly.express as px

import pandas as pd


def casualties_bar(dates, counts, title, x_title, y_title, color_scale=[[0, 'rgb(20, 20, 30)'], 
                                              [1, 'rgb(200, 0, 0)']]):
    
    
    max_count = counts.max()
    min_count = counts.min()
    normalized_counts = (counts - min_count) / (max_count - min_count)
    
    # Create a bar trace
    trace = go.Bar(
        x=dates,
        y=counts,
        marker=dict(
            color=normalized_counts,
            colorscale=color_scale,
            showscale=True,
            cmin=0,
            cmax=1
        )
    )
    
    # Create the layout
    layout = go.Layout(
        title=title,
        xaxis=dict(
            title=x_title,
            tickangle=45,
            automargin=True
        ),
        yaxis=dict(
            title=y_title
        ),
        bargap=0.2,
        width=1000, height=600,
        plot_bgcolor="#F0F0F0",
        paper_bgcolor="#F0F0F0"
    )
    
    return go.Figure(data=[trace], layout=layout)


def france_choropleth(df_dep, departements):
    fig = px.choropleth(df_dep, geojson=departements, color="casualties",
                        locations="departement", featureidkey="properties.nom",
                        projection="mercator", color_continuous_scale="Greys"
                       )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=1000, height=800)
    
    return fig



def density_plot(map_df):
    fig = px.density_mapbox(map_df, lat='latitude', lon='longitude', z='casualties', radius=10,
                        zoom=0, height=800, width=1000)

    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=46.603354, lon=1.888334),
            zoom=5
        ),
        showlegend=False
    )
    return fig



"""def france_choropleth(df_dep, departements):
    fig = go.Figure(data=go.Choropleth(
    geojson=departements,
    locations=df_dep['departement'],
    z=df_dep['casualties'],
    featureidkey="properties.nom",
    colorscale="Greys",
    colorbar=dict(len=0.6, y=0.5, title="Counts")))

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=1000, height=800)
    
    return fig"""


"""fig = px.choropleth(df_dep, geojson=departements, color="casualties",
                    locations="departement", featureidkey="properties.nom",
                    projection="mercator", color_continuous_scale="Greys"
                   )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=1000, height=600)"""