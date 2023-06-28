import dash
from dash import dcc, html, callback
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd
import re
from urllib.request import urlopen
import json
from plots import casualties_bar, france_choropleth, density_plot
from dash.dependencies import Input, Output, State
from datetime import datetime, date
from dateutil.relativedelta import relativedelta



tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}



# Data Wrangling
print("Loading main dataframe")
mdf_df = pd.read_csv('data/processed/mdf_df.csv')
print("Data wrangling")
mdf_df['pd_death_date'] = pd.to_datetime(mdf_df['pd_death_date'])

deaths_count = mdf_df.resample('1W', on='pd_death_date').size().reset_index()
deaths_count.columns = ['Date', 'Counts']
deaths_count['cumulative_sum'] = deaths_count['Counts'].cumsum()

df_departements = mdf_df.loc[mdf_df['annot_id_deces_pays_intitule'] == 'France']['annot_id_deces_departement_intitule']
df_departements = df_departements.str.replace(r'^\d+\s-\s', '', regex=True)
df_dep = df_departements.value_counts().reset_index().rename(columns={'annot_id_deces_departement_intitule': 'departement', 'count': 'casualties'})
df_dep['departement'] = df_dep['departement'].apply(lambda x: re.sub(r'\s*\([^)]*\)', '', x))

with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
    departements = json.load(response)

# Scattermap Plot Data
lieu_deces = pd.read_csv('lieu_deces_sel.csv').drop('Unnamed: 0', axis=1).dropna()
lieu_deces['coordinates'] = lieu_deces['coordinates'].apply(lambda x: tuple(float(num) for num in re.findall(r'[-+]?\d*\.\d+|\d+', x)))
lieu_deces['latitude'] = lieu_deces['coordinates'].apply(lambda x: x[0])
lieu_deces['longitude'] = lieu_deces['coordinates'].apply(lambda x: x[1])

df_France = mdf_df.loc[mdf_df['annot_id_deces_pays_intitule'] == 'France']
df_France['age_at_death']=pd.to_timedelta(df_France['age_at_death'])

df_lieu = df_France['annot_id_deces_lieu_intitule']
df_lieu_count = df_lieu.dropna().value_counts().reset_index()
map_df = df_lieu_count.merge(lieu_deces, on='annot_id_deces_lieu_intitule').rename(columns={'count': 'casualties'})

# Create the figures
print("Building plots")
casualties_fig = casualties_bar(deaths_count['Date'], deaths_count['Counts'], "Weekly French Casualties", None, "Number of Casualties")
cumulative_fig = casualties_bar(deaths_count['Date'], deaths_count['cumulative_sum'], "Cumulative Sum of Casualties", None, "Cumulative Sum of Casualties")
choropleth_fig = france_choropleth(df_dep, departements)
mapbox_plot = density_plot(map_df)

# Create the Dash application
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        
        dmc.DatePicker(
        id="date-picker",
        label="Birthdate",
        description="Enter your birthday, and odds are that there is someone who died for France at the exact same age as you are today during World War 1",
        minDate=date(1920, 1, 1),
        value=None,
        style={"width": 200},
        ),
        
        dmc.Space(h=10),
        dmc.Text(id="output-age"),
        dmc.Space(h=10),

        dcc.Tabs([
        dcc.Tab(dcc.Graph(id="casualties-graph",figure=casualties_fig), label="Casualties over time", 
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(dcc.Graph(id="cumulative-graph", figure=cumulative_fig), label="Casualties cumulated", 
            style=tab_style, selected_style=tab_selected_style)], style=tabs_styles),
        
        dcc.Tabs([
        dcc.Tab(dcc.Graph(id="choropleth", figure=choropleth_fig), label='Choropleth casualty map', 
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(dcc.Graph(id="density-mapbox", figure=mapbox_plot), label='Density casualty map', 
                style=tab_style, selected_style=tab_selected_style)], style=tabs_styles),          
 #       html.H2("Calculate Your Age"),
  #      html.Div(id="output-age", style={"margin-top": "1em"})      

    ],
    style={"margin": "1em 5em", "fontSize": 18}
)


"""@app.callback(
    Output("output-age", "children"),
    Input("date-picker", "date")
)
def get_alter_ego(selected_date):
    if selected_date is not None:
        birth_date = datetime.strptime(selected_date, '%Y-%m-%d')
        current_date = datetime.now().date()
        days_alive = (current_date - birth_date.date()).days
        select_alter = df_France.loc[df_France['age_at_death']==pd.to_timedelta(days_alive, unit='days')].sample()

        alter_ego = f'{select_alter.c_prenom.item()} {select_alter.c_nom.item()}, died at  {select_alter.annot_id_deces_lieu_intitule.item()}'
    return alter_ego"""

@callback(Output("output-age", "children"), Input("date-picker", "value"))
def get_alter_ego(selected_date):
    if selected_date is not None:
        birth_date = datetime.strptime(selected_date, '%Y-%m-%d')
        current_date = datetime.now().date()
        days_alive = (current_date - birth_date.date()).days
        select_alter = df_France.loc[df_France['age_at_death']==pd.to_timedelta(days_alive, unit='days')].sample()
        
        relative_time = relativedelta(current_date, birth_date)
        years = relative_time.years
        months = relative_time.months
        days = relative_time.days

        alter_ego = f'Aged ike you, at {years} years, {months} months and {days} days old, {select_alter.annot_id_grade_intitule.item()} {select_alter.c_prenom.item()} {select_alter.c_nom.item()}, died at  {select_alter.annot_id_deces_lieu_intitule.item()} in {select_alter.pd_death_date.item().strftime("%B %d, %Y")}'
        return alter_ego
    else: return ""


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
