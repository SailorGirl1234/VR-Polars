import csv
import decimal
import math
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from flask import Flask, flash, redirect, render_template, request, session, send_file, json
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Homepage
@app.route("/")
def index():
    return render_template("index.html")


# Wind data and output pages
@app.route("/wind", methods=["GET", "POST"])
def input():
    if request.method == "POST":

        # save data required into sail stats and polar function : boat,
        data_in = {}
        if not request.form.get("boat"):
            return render_template("index.html")
        data_in["boat"] = request.form.get("boat")

        # Remember wind details
        data_in["tws"] = str(request.form.get("windSpeed"))
        data_in["twa"] = int(request.form.get("windAngle"))
        # Remember selected sails
        data_in["light_wind"] = request.form.get("light")
        data_in["heavy_wind"] = request.form.get("heavy")
        data_in["reach"] = request.form.get("reach")
        data_in["foil"] = request.form.get("foils")
        data_in["polish"] = request.form.get("polish")

        # Create polar and collect sailing data recommendations
        data = sail_stats_and_polar(data_in)

        return render_template("output.html", data=data)

    else:

        #initialise all sails to 0
        sails = [
            {"name": "Jib", "speed": 0.0, "best_sail": "no"},
            {"name": "Spi", "speed": 0.0, "best_sail": "no"},
            {"name": "Light Jib", "speed": 0.0, "best_sail": "no"},
            {"name": "Light Gen", "speed": 0.0, "best_sail": "no"},
            {"name": "Staysail", "speed": 0.0, "best_sail": "no"},
            {"name": "Heavy Gen", "speed": 0.0, "best_sail": "no"},
            {"name": "Code 0", "speed": 0.0, "best_sail": "no"},
            {"optimum_upwind": {"sail": "", "speed": 0, "twa": 0}, "optimum_downwind": {"sail": "", "speed": 0, "twa": 0}}

        ]

        # Initialise all data to 0
        data = {
            "boat": "",
            "tws": "",
            "twa":  "",
            "sails": sails,
            "hullpolish": "",
            "foils": "",
            "boat": "",
            "light_wind": "",
            "heavy_wind": "",
            "reach": "",
            "foil": "",
            "polish": ""
        }
        return render_template("output.html", data=data)


# Display last saved polar
@app.route('/polar')
def show_polar():
    return render_template('polar.html')


# Show sailing and position data
@app.route("/position", methods=["GET", "POST"])
def position():

    # set initial scale of weather map
    zoominitial = 10

    if request.method == "POST":

        # collect position coordinats into latlon_dms dict (degrees mins secs)
        latlon_dms = {}
        latlon_dms["lat_d"] = int(request.form.get("lat_deg"))
        latlon_dms["lat_m"] = int(request.form.get("lat_min"))
        latlon_dms["lat_s"] = int(request.form.get("lat_sec"))
        latlon_dms["lat_H"] = request.form.get("n_s")

        latlon_dms["lon_d"] = int(request.form.get("lon_deg"))
        latlon_dms["lon_m"] = int(request.form.get("lon_min"))
        latlon_dms["lon_s"] = int(request.form.get("lon_sec"))
        latlon_dms["lon_H"] = request.form.get("e_w")

        # convert deg min sec position data into decimal degrees
        latlon_decimal = deg_dms2decimal(latlon_dms)

        # fetch wind data for given position
        wind_data = get_wind_data(latlon_decimal[0], latlon_decimal[1])

        # remember boat name in data_in dictionary
        data_in = {}
        if not request.form.get("boat"):
            return render_template("index.html")
        data_in["boat"] = request.form.get("boat")

        # Remember wind details
        data_in["tws"] = str(wind_data["speed"])

        # Calculate true wind angle (true wind direction - heading) convert to between 0 and 180 degrees relative to your direction of travel
        heading = int(request.form.get("heading"))
        rwa = wind_data["deg"] - heading
        tack = "Port"
        if rwa < 0:
            rwa += 360
        if rwa > 180:
            rwa -= 180
            rwa = 180 - rwa
            tack = "Starboard"
        data_in["twa"] = rwa

        # Remember selected sails
        data_in["light_wind"] = request.form.get("light")
        data_in["heavy_wind"] = request.form.get("heavy")
        data_in["reach"] = request.form.get("reach")
        data_in["foil"] = request.form.get("foils")
        data_in["polish"] = request.form.get("polish")

        # create polar diagram and calculate sailing info
        data = sail_stats_and_polar(data_in)

        return render_template("position.html", tack=tack, lat_decimal=latlon_decimal[0], lon_decimal=latlon_decimal[1], zoominitial=zoominitial, latlon_dms=latlon_dms, data=data, heading=heading)
    else:

        # initialise map to bramble bank
        lat_decimal = 50.7917
        lon_decimal = -1.29023

        # convert decimal degrees to degrees mins secs
        latlon_dms = deg_decimal2dms(lat_decimal, lon_decimal)

        return render_template("dms.html", lat_decimal=lat_decimal, lon_decimal=lon_decimal, zoominitial=zoominitial, latlon_dms=latlon_dms)


@app.route("/decimal", methods=["GET", "POST"])
def decimal():
    if request.method == "POST":
        # initialise weather map scale
        zoominitial = 10

        # fetch form data (lat, long, heading)
        lat_decimal = float(request.form.get("lat_decimal"))
        lon_decimal = float(request.form.get("lon_decimal"))
        heading = request.form.get("heading")

        # convert lat long from decimal degrees to deg mins sec
        latlon_dms = deg_decimal2dms(lat_decimal, lon_decimal)

        # fetch win data from given location
        wind_data = get_wind_data(lat_decimal, lon_decimal)

        # remember boat type
        data_in = {}
        if not request.form.get("boat"):
            return render_template("index.html")
        data_in["boat"] = request.form.get("boat")

        # Remember wind details
        data_in["tws"] = str(wind_data["speed"])

        # Calculate relative wind angle
        heading = int(request.form.get("heading"))
        rwa = wind_data["deg"] - heading
        tack = "Port"
        if rwa < 0:
            rwa += 360
        if rwa > 180:
            rwa -= 180
            rwa = 180 - rwa
            tack = "Starboard"
        data_in["twa"] = rwa
        print("relative wind angle: " + str(data_in["twa"]) + "wind speed: " + str(data_in["tws"]))

        # Remember selected sails
        data_in["light_wind"] = request.form.get("light")
        data_in["heavy_wind"] = request.form.get("heavy")
        data_in["reach"] = request.form.get("reach")
        data_in["foil"] = request.form.get("foils")
        data_in["polish"] = request.form.get("polish")

        # create polar chart and calculate sailing stats
        data = sail_stats_and_polar(data_in)

        return render_template("position.html", tack=tack, lat_decimal=lat_decimal, lon_decimal=lon_decimal, zoominitial=zoominitial, latlon_dms=latlon_dms, heading=heading, data=data)
    else:
        # initialise wind map
        lat_decimal = 50.7917
        lon_decimal = -1.29023
        zoominitial = 10

        return render_template("decimal.html", lat_decimal=lat_decimal, lon_decimal=lon_decimal, zoominitial=zoominitial)


# convert decimal degrees to degrees mins and secs
def deg_decimal2dms(lat, lon):
    latlon_dms = {}
    # select hemisphere
    if lat > 0:
        latlon_dms["lat_H"] = 'N'
    else:
        latlon_dms["lat_H"] = 'S'
        lat = -lat

    if lon > 0:
        latlon_dms["lon_H"] = 'E'
    else:
        latlon_dms["lon_H"] = 'W'
        lon = -lon

    # select degrees
    latlon_dms["lat_d"] = int(lat)
    latlon_dms["lon_d"] = int(lon)

    # calculate mins
    latlon_dms["lat_m"] = int((lat - latlon_dms["lat_d"])*60)
    latlon_dms["lon_m"] = int((lon - latlon_dms["lon_d"])*60)

    # calculate secs
    latlon_dms["lat_s"] = int((((lat - latlon_dms["lat_d"])*60)-latlon_dms["lat_m"])*60)
    latlon_dms["lon_s"] = int((((lon - latlon_dms["lon_d"])*60)-latlon_dms["lon_m"])*60)

    return latlon_dms


# convert degrees mins secs to decimal degrees
def deg_dms2decimal(latlon_dms):
    lat_decimal = latlon_dms["lat_d"] + (latlon_dms["lat_m"]/60) + (latlon_dms["lat_s"]/3600)
    lon_decimal = latlon_dms["lon_d"] + (latlon_dms["lon_m"]/60) + (latlon_dms["lon_s"]/3600)

    # calculate if +ive or -ve depending on hemisphere
    if latlon_dms["lat_H"] == "S":
        lat_decimal = - lat_decimal
    if latlon_dms["lon_H"] == "W":
        lon_decimal = - lon_decimal
    return lat_decimal, lon_decimal


# calculate wind speed and direction from wind vectors
def wind_vectors2speedAngle(u_ms, v_ms):
    # a^2 + b^2 = c^2 - calculate wind speed
    wind_abs = math.sqrt(u_ms ^ 2 + v_ms ^ 2)

    # calculate wind angle
    wind_dir_trig_to = math.acosatan2(u_ms/wind_abs, v_ms/wind_abs)
    wind_dir_trig_to_degrees = wind_dir_trig_to * 180/math.pi
    wind_dir_trig_from_degrees = wind_dir_trig_to_degrees + 180
    wind_dir_cardinal = 90 - wind_dir_trig_from_degrees

    # convert speed from m/s to knots
    speed_kts = wind_abs * 1.94384

    return speed_kts, wind_dir_cardinal


# get wind data from open weather map
def get_wind_data(lat_decimal, lon_decimal):

    lat_decimal = round(lat_decimal, 2)
    lon_decimal = round(lon_decimal, 2)

    # Send post request to open weather map for point forecast
    try:
        API_key = "54ee4e4b0fd90973e261b896df65fd1a"
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat_decimal}&lon={lon_decimal}&appid={API_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        print("no wind data available for that location")

    try:
        # save required data from responce in wind dictionary
        wind = {}

        data = response.json()
        wind["speed"] = data["wind"]["speed"]
        wind["deg"] = data["wind"]["deg"]
        wind["speed"] = round(wind["speed"] * 1.94384)

        return wind
    except requests.RequestException:
        print("data not loaded properly")


# create polar chart and compute sailing data
def sail_stats_and_polar(data_in):
    # retrieve info
    boat = data_in["boat"]

    # Remember wind details
    tws = data_in["tws"]
    twa = data_in["twa"]

    # Initialise settings
    fig = go.Figure()
    sails = [
        {"name": "Jib", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"name": "Spi", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"name": "Light Jib", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"name": "Light Gen", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"name": "Staysail", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"name": "Heavy Gen", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"name": "Code 0", "speed": 0.0, "best_sail": "no", "vmg":
            {"speed_upwind": 0, "twa_upwind": 0, "speed_downwind": 0, "twa_downwind": 0, "max_speed": 0}},
        {"optimum_upwind": {"sail": "", "speed": 0, "twa": 0}, "optimum_downwind": {"sail": "", "speed": 0, "twa": 0}, "max_speed": 0}
    ]
    hullpolish = "none"
    foils = "none"
    HULLPOLISH = 1.0

    # check which extras were selected
    light_wind = data_in["light_wind"]
    heavy_wind = data_in["heavy_wind"]
    reach = data_in["reach"]
    foil = data_in["foil"]
    polish = data_in["polish"]
    HULLPOLISH = 1.0
    if polish:
        # apply speed factor if hullpolish selected
        HULLPOLISH = 1.003

    # create list of all wind angles
    wind_angles = list(range(181))

    # compute standard sails - [0]Jib and [1]Spi - if foils selected or not - read csv into memory - select speed for specified wind angle and strength - compute VMG data
    if foil:
        foils = "yes"
        jib = pd.read_csv(f"static/polars/{boat}/{boat}_Jib.csv", sep=";")
        sails[0]["speed"] = jib.loc[twa, tws]
        sails[0]["vmg"] = vmg(jib, tws, HULLPOLISH)

        spi = pd.read_csv(f"static/polars/{boat}/{boat}_Spi.csv", sep=";")
        sails[1]["speed"] = spi.loc[twa, tws]
        sails[1]["vmg"] = vmg(spi, tws, HULLPOLISH)

    else:
        foils = "no"
        jib = pd.read_csv(f"static/polars/{boat}/{boat}Jib.csv", sep=";")
        sails[0]["speed"] = jib.loc[twa, tws]
        sails[0]["vmg"] = vmg(jib, tws, HULLPOLISH)

        spi = pd.read_csv(f"static/polars/{boat}/{boat}Spi.csv", sep=";")
        sails[1]["speed"] = spi.loc[twa, tws]
        sails[1]["vmg"] = vmg(spi, tws, HULLPOLISH)

    # plot on polar chart
    fig.add_trace(go.Scatterpolar(
        r=round(jib[tws]*HULLPOLISH, 2),
        theta=wind_angles,
        mode='lines',
        name='Jib',
        line_color='#003f5c'
    ))
    fig.add_trace(go.Scatterpolar(
        r=round(spi[tws]*HULLPOLISH, 2),
        theta=wind_angles,
        mode='lines',
        name='Spi',
        line_color='#2f4b7c'
    ))

    # compute lightwind sails if selected- [2]LightJib and [3]LightGen - if foils selected or not - read csv into memory - select speed for specified wind angle and strength - compute VMG data
    if light_wind:
        light_wind = "checked"
        if foil:
            lightJib = pd.read_csv(f"static/polars/{boat}/{boat}_LightJib.csv", sep=";")
            sails[2]["speed"] = lightJib.loc[twa, tws]
            sails[2]["vmg"] = vmg(lightJib, tws, HULLPOLISH)

            lightGen = pd.read_csv(f"static/polars/{boat}/{boat}_LightGen.csv", sep=";")
            sails[3]["speed"] = lightGen.loc[twa, tws]
            sails[3]["vmg"] = vmg(lightGen, tws, HULLPOLISH)

        else:
            lightJib = pd.read_csv(f"static/polars/{boat}/{boat}LightJib.csv", sep=";")
            sails[2]["speed"] = lightJib.loc[twa, tws]
            sails[2]["vmg"] = vmg(lightJib, tws, HULLPOLISH)

            lightGen = pd.read_csv(f"static/polars/{boat}/{boat}LightGen.csv", sep=";")
            sails[3]["speed"] = lightGen.loc[twa, tws]
            sails[3]["vmg"] = vmg(lightGen, tws, HULLPOLISH)

        # plot on polar chart
        fig.add_trace(go.Scatterpolar(
            r=round(lightJib[tws]*HULLPOLISH, 2),
            theta=wind_angles,
            mode='lines',
            name='Light Jib',
            line_color='#665191'
        ))
        fig.add_trace(go.Scatterpolar(
            r=round(lightGen[tws]*HULLPOLISH, 2),
            theta=wind_angles,
            mode='lines',
            name='Light Gen',
            line_color='#a05195'
        ))
    else:
        light_wind = ""

    # compute heavywind sails if selected- [4]Staysail and [5]HeavyGen - if foils selected or not - read csv into memory - select speed for specified wind angle and strength - compute VMG data
    if heavy_wind:
        heavy_wind = "checked"
        if foil:
            staysail = pd.read_csv(f"static/polars/{boat}/{boat}_Stay.csv", sep=";")
            sails[4]["speed"] = staysail.loc[twa, tws]
            sails[4]["vmg"] = vmg(staysail, tws, HULLPOLISH)

            heavyGen = pd.read_csv(f"static/polars/{boat}/{boat}_HeavyGen.csv", sep=";")
            sails[5]["speed"] = heavyGen.loc[twa, tws]
            sails[5]["vmg"] = vmg(heavyGen, tws, HULLPOLISH)

        else:
            staysail = pd.read_csv(f"static/polars/{boat}/{boat}Stay.csv", sep=";")
            sails[4]["speed"] = staysail.loc[twa, tws]
            sails[4]["vmg"] = vmg(staysail, tws, HULLPOLISH)

            heavyGen = pd.read_csv(f"static/polars/{boat}/{boat}HeavyGen.csv", sep=";")
            sails[5]["speed"] = heavyGen.loc[twa, tws]
            sails[5]["vmg"] = vmg(heavyGen, tws, HULLPOLISH)

        # plot on polar chart
        fig.add_trace(go.Scatterpolar(
            r=round(staysail[tws]*HULLPOLISH, 2),
            theta=wind_angles,
            mode='lines',
            name='Staysail',
            line_color='#d45087'
        ))
        fig.add_trace(go.Scatterpolar(
            r=round(heavyGen[tws]*HULLPOLISH, 2),
            theta=wind_angles,
            mode='lines',
            name='Heavy Gen',
            line_color='#f95d6a'
        ))
    else:
        heavy_wind = ""

    # compute reaching sails if selected- [6]code0 - if foils selected or not - read csv into memory - select speed for specified wind angle and strength - compute VMG data
    if reach:
        reach = "checked"
        if foil:
            code0 = pd.read_csv(f"static/polars/{boat}/{boat}_Code0.csv", sep=";")
            sails[6]["speed"] = code0.loc[twa, tws]
            sails[6]["vmg"] = vmg(code0, tws, HULLPOLISH)

        else:
            code0 = pd.read_csv(f"static/polars/{boat}/{boat}Code0.csv", sep=";")
            sails[6]["speed"] = code0.loc[twa, tws]
            sails[6]["vmg"] = vmg(code0, tws, HULLPOLISH)

        # plot on polar chart
        fig.add_trace(go.Scatterpolar(
            r=round(code0[tws]*HULLPOLISH,2),
            theta=wind_angles,
            mode='lines',
            name='Code 0',
            line_color='#ff7c43'
        ))
    else:
        reach = ""

    # if hull polish activated - speed factor 1.003
    if polish:
        polish = "checked"
        hullpolish = "yes"
        for i in range(0, 7):
            sails[i]["speed"] *= HULLPOLISH

            # Compare vmgs for each sail and find optimum
            if sails[i]["vmg"]["speed_upwind"] > sails[7]["optimum_upwind"]["speed"]:
                sails[7]["optimum_upwind"]["speed"] = sails[i]["vmg"]["speed_upwind"]
                sails[7]["optimum_upwind"]["twa"] = sails[i]["vmg"]["twa_upwind"]
                sails[7]["optimum_upwind"]["sail"] = sails[i]["name"]
            if sails[i]["vmg"]["speed_downwind"] > sails[7]["optimum_downwind"]["speed"]:
                sails[7]["optimum_downwind"]["speed"] = sails[i]["vmg"]["speed_downwind"]
                sails[7]["optimum_downwind"]["twa"] = sails[i]["vmg"]["twa_downwind"]
                sails[7]["optimum_downwind"]["sail"] = sails[i]["name"]
            if sails[i]["vmg"]["max_speed"] > sails[7]["max_speed"]:
                sails[7]["max_speed"] = sails[i]["vmg"]["max_speed"]

    else:
        polish = ""
        hullpolish = "no"
        # Compare vmgs for each sail and find optimum
        for i in range(7):
            if sails[i]["vmg"]["speed_upwind"] > sails[7]["optimum_upwind"]["speed"]:
                sails[7]["optimum_upwind"]["speed"] = sails[i]["vmg"]["speed_upwind"]
                sails[7]["optimum_upwind"]["twa"] = sails[i]["vmg"]["twa_upwind"]
                sails[7]["optimum_upwind"]["sail"] = sails[i]["name"]
            if sails[i]["vmg"]["speed_downwind"] > sails[7]["optimum_downwind"]["speed"]:
                sails[7]["optimum_downwind"]["speed"] = sails[i]["vmg"]["speed_downwind"]
                sails[7]["optimum_downwind"]["twa"] = sails[i]["vmg"]["twa_downwind"]
                sails[7]["optimum_downwind"]["sail"] = sails[i]["name"]
            if sails[i]["vmg"]["max_speed"] > sails[7]["max_speed"]:
                sails[7]["max_speed"] = sails[i]["vmg"]["max_speed"]

    if foil:
        foil = "checked"
    else:
        foil = ""

    # round to 2 decimal places and find best sail choice
    best = {'sail_id': -1, 'speed': 0}
    for i in range(0, 7):
        sails[i]["speed"] = round(sails[i]["speed"], 2)
        if sails[i]["speed"] > best["speed"]:
            best["sail_id"] = i
            best["speed"] = sails[i]["speed"]
    sails[best["sail_id"]]["best_sail"] = "best_sail"

    #set polar chart display settings
    fig.update_polars(
        angularaxis_direction="clockwise",
        radialaxis_angle=90,
        radialaxis_tickangle=0,
        radialaxis_side="counterclockwise",
        radialaxis_title_text="(kts)",
        bgcolor="Gainsboro",
        sector=[-90, 90]
    )

    fig.update_layout(
        title=f"<b>{boat}</b><br>TWS: {tws}kts - RWA: {str(twa)}° <br>Foils: {foils} - Hull polish: {hullpolish}",
        title_xref="container",
        title_x=0.5,
        title_xanchor="center",
        font_size=10,
        showlegend=True,
        legend_orientation="h",
        paper_bgcolor="WhiteSmoke",
        width=500,
        height=700,
    )

    fig.update_traces(
        hovertemplate="RWA: %{theta}" "<br>Boat Speed: %{r}kts"
    )

    # add wind angle line
    fig.add_trace(go.Scatterpolar(
        r=[0, sails[7]["max_speed"]/2, sails[7]["max_speed"]*1.05],
        theta=[twa, twa, twa],
        mode='lines',
        name='Wind Angle',
        line_dash="dashdot",
        hovertemplate="TWA: %{theta}",
        line_color='#ffa600',
    ))

    # add vmg lines
    fig.add_trace(go.Scatterpolar(
        r=[sails[7]["max_speed"]*1.05, sails[7]["max_speed"]/2, 0],
        theta=[sails[7]["optimum_downwind"]["twa"], sails[7]["optimum_downwind"]["twa"], sails[7]["optimum_downwind"]["twa"]],
        mode='lines',
        name='Optimum',
        line_dash="dot",
        showlegend=False,
        hovertemplate="Downwind Heading: %{theta}" "<br>Downwind VMG: " + str(sails[7]['optimum_downwind']['speed']) + "kts",
        line_color='#ff0000',
    ))
    fig.add_trace(go.Scatterpolar(
        r=[0, sails[7]["max_speed"]/2, sails[7]["max_speed"]*1.05],
        theta=[sails[7]["optimum_upwind"]["twa"], sails[7]["optimum_upwind"]["twa"], sails[7]["optimum_upwind"]["twa"]],
        mode='lines',
        name='Optimum',
        line_dash="dot",
        showlegend=False,
        hovertemplate="Upwind Heading: %{theta}" "<br>Upwind VMG: " + str(sails[7]['optimum_upwind']['speed']) + "kts",
        line_color='#ff0000',
    ))

    # save polar chart as an html file
    fig.write_html("templates/polar.html", include_plotlyjs="cdn")

    # save saining info into data dictionary
    data = {
        "boat": boat,
        "tws": tws,
        "twa": twa,
        "sails": sails,
        "hullpolish": hullpolish,
        "foils": foils,
        "boat": data_in["boat"],
        "light_wind": light_wind,
        "heavy_wind": heavy_wind,
        "reach": reach,
        "foil": foil,
        "polish": polish
    }

    return data


# calculate VMGs
def vmg(sail, tws, HULLPOLISH):
    vmg_best = {
        "speed_upwind": 0,
        "twa_upwind": 0,
        "speed_downwind": 0,
        "twa_downwind": 0,
        "max_speed": 0
    }
    for i in range(len(sail)):
        vmg = round((sail.loc[i, tws]*HULLPOLISH) * math.cos(math.radians(i)), 2)
        # find best upwind VMG angle and speed
        if i < 90 and vmg > vmg_best["speed_upwind"]:
            vmg_best["speed_upwind"] = vmg
            vmg_best["twa_upwind"] = i

        # find best downwind VMG angle and speed
        elif i > 90 and vmg < vmg_best["speed_downwind"]:
            vmg_best["speed_downwind"] = vmg
            vmg_best["twa_downwind"] = i

        # find max speed at set wind strength
        if round(sail.loc[i, tws]*HULLPOLISH, 2) > vmg_best["max_speed"]:
            vmg_best["max_speed"] = round(sail.loc[i, tws]*HULLPOLISH, 2)

    vmg_best["speed_downwind"] = -vmg_best["speed_downwind"]

    return vmg_best
