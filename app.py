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





app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Data Feature Store"
server = app.server


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

# Dictionary of important locations in New York
list_of_locations = {
    "016-D_001": {"lat": 40.7505, "lon": -73.9934},
    "016-D_002": {"lat": 40.8296, "lon": -73.9262},
    "016-D_003": {"lat": 40.7484, "lon": -73.9857},
    "016-D_004": {"lat": 40.7069, "lon": -74.0113},
    "016-D_005": {"lat": 40.644987, "lon": -73.785607},
    "016-D_006": {"lat": 40.7527, "lon": -73.9772},
    "016-D_007": {"lat": 40.7589, "lon": -73.9851},
    "016-D_008": {"lat": 40.8075, "lon": -73.9626},
    "016-D_009": {"lat": 40.7489, "lon": -73.9680},
}

list_of_data_sources = {
    "ATMS": {"lat": 40.7505, "lon": -73.9934},
    "SRMS": {"lat": 40.8296, "lon": -73.9262},
    "SCATS": {"lat": 40.7484, "lon": -73.9857},
    "TomTom": {"lat": 40.7069, "lon": -74.0113},
}

# Initialize data frame
df1 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv",
    dtype=object,
)
df2 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data2.csv",
    dtype=object,
)
df3 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data3.csv",
    dtype=object,
)
df = pd.concat([df1, df2, df3], axis=0)
df["Date/Time"] = pd.to_datetime(df["Date/Time"], format="%Y-%m-%d %H:%M")
df.index = df["Date/Time"]
df.drop("Date/Time", 1, inplace=True)
totalList = []
for month in df.groupby(df.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
totalList = np.array(totalList)

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
                                            # options=[
                                            #     {"label": i, "value": i}
                                            #     for i in list_of_locations
                                            # ],
                                            options=dropdown_options,
                                            placeholder="Select locations",
                                            multi= True,
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select hours",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
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
                            ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2023, 9, 30),
                                    initial_visible_month=dt(2022, 10, 11),
                                    date=dt(2022, 10, 11).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
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

# Gets the amount of days in the specified month
# Index represents month (0 is April, 1 is May, ... etc.)
daysInMonth = [30, 31, 30, 31, 31, 30]

# Get index for the specified month in the dataframe
monthIndex = pd.Index(["Apr", "May", "June", "July", "Aug", "Sept"])

# Get the amount of rides per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_selection(month, day, selection):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of rides at a particular time
        yVal.append(len(totalList[month][day][totalList[month][day].index.hour == i]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]





# Get the Coordinates of the chosen months, dates and times
def getLatLonColor(selectedData, month, day):
    listCoords = totalList[month][day]

    # No times selected, output all times for chosen month and date
    if selectedData is None or len(selectedData) is 0:
        return listCoords
    listStr = "listCoords["
    for time in selectedData:
        if selectedData.index(time) is not len(selectedData) - 1:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ") | "
        else:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ")]"
    return eval(listStr)


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
# @app.callback(
#     Output("map-container", "figure"),
#     [
#         Input("date-picker", "date"),
#         Input("bar-selector", "value"),
#         Input("drop_box_roadid", "value"),
#         Input("source-dropdown", "value"),
#     ],
# )
# def update_graph(datePicked, selectedData, selectedLocation):
#     zoom = 12.0
#     latInitial = 40.7272
#     lonInitial = -73.991251
#     bearing = 0

#     if selectedLocation:
#         zoom = 15.0
#         latInitial = list_of_locations[selectedLocation]["lat"]
#         lonInitial = list_of_locations[selectedLocation]["lon"]

#     date_picked = dt.strptime(datePicked, "%Y-%m-%d")
#     monthPicked = date_picked.month - 4
#     dayPicked = date_picked.day - 1
#     listCoords = getLatLonColor(selectedData, monthPicked, dayPicked)

#     return go.Figure(
#         data=[
#             # Data for all rides based on date and time
#             Scattermapbox(
#                 lat=listCoords["Lat"],
#                 lon=listCoords["Lon"],
#                 mode="markers",
#                 hoverinfo="lat+lon+text",
#                 text=listCoords.index.hour,
#                 marker=dict(
#                     showscale=True,
#                     color=np.append(np.insert(listCoords.index.hour, 0, 0), 23),
#                     opacity=0.5,
#                     size=5,
#                     colorscale=[
#                         [0, "#F4EC15"],
#                         [0.04167, "#DAF017"],
#                         [0.0833, "#BBEC19"],
#                         [0.125, "#9DE81B"],
#                         [0.1667, "#80E41D"],
#                         [0.2083, "#66E01F"],
#                         [0.25, "#4CDC20"],
#                         [0.292, "#34D822"],
#                         [0.333, "#24D249"],
#                         [0.375, "#25D042"],
#                         [0.4167, "#26CC58"],
#                         [0.4583, "#28C86D"],
#                         [0.50, "#29C481"],
#                         [0.54167, "#2AC093"],
#                         [0.5833, "#2BBCA4"],
#                         [1.0, "#613099"],
#                     ],
#                     colorbar=dict(
#                         title="Time of<br>Day",
#                         x=0.93,
#                         xpad=0,
#                         nticks=24,
#                         tickfont=dict(color="#d8d8d8"),
#                         titlefont=dict(color="#d8d8d8"),
#                         thicknessmode="pixels",
#                     ),
#                 ),
#             ),
#             # Plot of important locations on the map
#             Scattermapbox(
#                 lat=[list_of_locations[i]["lat"] for i in list_of_locations],
#                 lon=[list_of_locations[i]["lon"] for i in list_of_locations],
#                 mode="markers",
#                 hoverinfo="text",
#                 text=[i for i in list_of_locations],
#                 marker=dict(size=8, color="#ffa0a0"),
#             ),
#         ],
#         layout=Layout(
#             autosize=True,
#             margin=go.layout.Margin(l=0, r=35, t=0, b=0),
#             showlegend=False,
#             mapbox=dict(
#                 accesstoken=mapbox_access_token,
#                 center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
#                 style="dark",
#                 bearing=bearing,
#                 zoom=zoom,
#             ),
#             updatemenus=[
#                 dict(
#                     buttons=(
#                         [
#                             dict(
#                                 args=[
#                                     {
#                                         "mapbox.zoom": 12,
#                                         "mapbox.center.lon": "-73.991251",
#                                         "mapbox.center.lat": "40.7272",
#                                         "mapbox.bearing": 0,
#                                         "mapbox.style": "dark",
#                                     }
#                                 ],
#                                 label="Reset Zoom",
#                                 method="relayout",
#                             )
#                         ]
#                     ),
#                     direction="left",
#                     pad={"r": 0, "t": 0, "b": 0, "l": 0},
#                     showactive=False,
#                     type="buttons",
#                     x=0.45,
#                     y=0.02,
#                     xanchor="left",
#                     yanchor="bottom",
#                     bgcolor="#323130",
#                     borderwidth=1,
#                     bordercolor="#6d6d6d",
#                     font=dict(color="#FFFFFF"),
#                 )
#             ],
#         ),
#     )

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
