import os
import json

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_deck
import pydeck as pdk
import geopandas as gpd


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



map_data_df = read_map_df("RAMM_Carriageway_Segments_NZTA.geojson") # map data set

all_roadid = list(map_data_df["name"])# get a list of the road id from the "map_data_df"

dropdown_options = [{"label": roadid,"value": roadid} for roadid in all_roadid] # for dropdown box options

mapbox_api_token = "pk.eyJ1Ijoicml2aW5kdSIsImEiOiJjazZpZXo0amUwMGJ1M21zYXpzZGMzczdiIn0.eoArFYnhz0jEPQEnF0vdKQ" #For the base map token

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [ 
        html.Div(
            id = "text_header",
            style = {"textAlign": "center", "color":"green"},
            children =[
                html.H1("DFS MAP"),
                    html.Hr()
                    ]
        ),
    html.Div(
        id = "right_section",
        style = {
            "width" : "20%",
            "height": "95vh",
            "float": "right",
            "display": "inline-block",
            "position": "relative",

        },
        children = [
            html.Div(
                id = "drop_box_section",     # div section for drop down box
                children = [
                    html.H5("Road Id: "),
                    dcc.Dropdown(
                        id = "drop_box_roadid",
                        options=dropdown_options,
                        multi= True,
                        
                    ),
                ],
            ),
            
        ],
    ),
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
    ]
)
# call back section for updating the map(path color)

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
    app.run_server()