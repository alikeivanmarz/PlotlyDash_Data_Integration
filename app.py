import os
import json

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash import dcc
from dash import html
import dash_deck
import pydeck as pdk
import geopandas as gpd

import pandas as pd
import numpy as np

from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt


# get data from geoJson file
def read_map_df(path):
    color = [209,42,33]
    geo_map_df = gpd.read_file(path)
    map_df = gpd.GeoDataFrame()
    map_df["geometry"] = geo_map_df.geometry
    map_df["name"] = geo_map_df.filtered_road_id
    color_list = [color]*len(map_df["name"])
    map_df["color"] = color_list
    return map_df
    

# create a layer for the map
def get_deck(map_data_df):
    # Set the viewport location
    view_state = pdk.ViewState(latitude=-36.859067426240394, longitude=174.76020812611904, zoom=12)

    # Define a layer to display on a map
    layer = pdk.Layer(
        "PathLayer",
        map_data_df,
        pickable = True,
        get_color="color",
        width_scale = 2.5,
        width_min_pixels = 2,
        get_path = "geometry.coordinates",
        get_width = 2,
    )
    # Render
    # Start building the layout here
    r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    return r

# Update color for the seleted path
def update_color(h):
    return [50,168,82]



map_data_df = read_map_df("assets/RAMM_Carriageway_Segments_NZTA.geojson") # map data set

all_roadid = list(map_data_df["name"])# get a list of the road id from the "map_data_df"

dropdown_options = [{"label": roadid,"value": roadid} for roadid in all_roadid] # for dropdown box options

mapbox_api_token = "pk.eyJ1Ijoicml2aW5kdSIsImEiOiJjazZpZXo0amUwMGJ1M21zYXpzZGMzczdiIn0.eoArFYnhz0jEPQEnF0vdKQ" #For the base map token

list_of_data_sources = {
    "ATMS",
    "SRMS",
}

list_of_resolution = {
    "5MIN",
    "15MIN",
    "30MIN",
    "1H",
}

list_of_metrics = {
    "Volume",
    "Travel Time",
}

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Data Feature Store"
server = app.server


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"



# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src=app.get_asset_url("Wsp_red.png"),
                            ),
                            href="https://www.wsp.com/en-nz/",
                        ),
                        html.H2("DASH - DATA FEATURE STORE"),
                        html.P(
                            """Select site locations from the dropdown or map."""
                        ),
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="drop_box_roadid",
                                            options=dropdown_options,
                                            placeholder="Select locations",
                                            multi= True,
                                        )
                                    ],
                                ),
                                # html.Div(
                                #     className="div-for-dropdown",
                                #     children=[
                                #         # Dropdown to select times
                                #         dcc.Dropdown(
                                #             id="bar-selector",
                                #             options=[
                                #                 {
                                #                     "label": str(n) + ":00",
                                #                     "value": str(n),
                                #                 }
                                #                 for n in range(24)
                                #             ],
                                #             multi=True,
                                #             placeholder="Select hours",
                                #         )
                                #     ],
                                # ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(
                                            id="source-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_data_sources
                                            ],
                                            placeholder="Select Data Source",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(
                                            id="resolution-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_resolution
                                            ],
                                            placeholder="Select Resolution",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(
                                            id="metrics-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_metrics
                                            ],
                                            placeholder="Select Metrics",
                                        )
                                    ],
                                ),
                            ],
                        ),                     
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker-from",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2023, 12, 30),
                                    # initial_visible_month=dt(2022, 10, 11),
                                    placeholder="Select Date From",
                                    # date=dt(2022, 10, 11).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker-to",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2023, 12, 30),
                                    # initial_visible_month=dt(2022, 10, 11),
                                    placeholder="Select Date To",
                                    # date=dt(2022, 10, 11).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        dcc.Markdown(
                            """
                            Data Source: [Download](https://github.com/fivethirtyeight/uber-tlc-foil-response/tree/master/uber-trip-data)

                            """
                        ),
                    ],
                ),
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            id='map-container',
                            style={
                                "width": "80%",
                                "height": "95vh",
                                "float": "left",
                                "display": "inline-block",
                                "position": "relative",
                            },
                            children=[
                                dash_deck.DeckGL(
                                    get_deck(map_data_df).to_json(), # div section for map display
                                    id="deck",
                                    tooltip={"text": "{name}"},
                                    mapboxKey = mapbox_api_token,
                                    enableEvents=['click']
                                )
                            
                            ],
                        ),                 
                        # dcc.Graph(id="map-graph"),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any locations from the map."
                            ],
                        ),
                        # dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        )
    ]
)



@app.callback(
    Output('map-container','children'),
    [Input('drop_box_roadid', 'value')]
)
def update_graph(value):
    #print(value)
   
    if value == None or value ==[]:
        return dash_deck.DeckGL(
                    get_deck(map_data_df).to_json(),
                    id="deck",
                    tooltip={"text": "{name}"},
                    mapboxKey = mapbox_api_token,
                    enableEvents=['click']
                )
    else:
       
        new_map_df = map_data_df.copy()
        for element in value:
            new_map_df["color"][new_map_df.name == element]  = new_map_df["color"][new_map_df.name == element].apply(update_color)
        return dash_deck.DeckGL(
                    get_deck(new_map_df).to_json(),
                    id="deck",
                    tooltip={"text": "{name}"},
                    mapboxKey = mapbox_api_token,
                    enableEvents=['click']
                )
#call back fuction for updating drop down box
@app.callback(
    Output("drop_box_roadid","value"),   
    [Input("deck", "clickInfo"),State("drop_box_roadid","value")]
)
def check(clickInfo,value):
    
    if value == None and clickInfo == None:
        return None
    elif value == None:
        return [clickInfo["object"]["name"]]
    else:
        if clickInfo["object"]["name"] in value:
            value.remove(clickInfo["object"]["name"])
        else:
            value.append(clickInfo["object"]["name"])
        return list(set(value))
    

if __name__ == "__main__":
    app.run_server(debug=True)
