# **VR POLARS**

## **Video Demo:**  [https://youtu.be/13EdunA8D1U](https://youtu.be/13EdunA8D1U)

## **Description:**

**VR Polars** is designed to be used as a reference tool whilst playing the [*Virtual Regatta Offshore*](https://www.virtualregatta.com/en/) sailing racing game.
It shows the user what boat speed is expected, and which sail is best to use, given a certain wind speed and direction.

### **Technologies used**

The VR Polars web app makes use of the following languages and technologies:

- Python
- Flask
- Javascript
- HTML
- CSS

incorporating Plotty, Pandas, Jinja2, Bootstrap4 and Leaflet

### **How to use the webapp**

#### **Inputting wind data**

From the home page or the *Wind Data* link, the user can select which boat they are racing in, and then input the wind speed
and the wind angle relative to their boat.

The user can then select which *extras* they wish to use. The extra sail sets, foils and hull polish correspond to the add
ons that can be selected within the *Virtual Regatta Offshore* game. If no extras are selected,
only information on the basic sail set (Jib and Spi) will be shown.

#### **Sailing data displayed**

Once submitted, the user is then shown a table displaying the boat speed expected for each selected sail set up, at the inputted wind angle and wind speed.
The best suited sail for these conditions is highlighted within this table.

The optimum upwind and downwind set up for that wind speed is also shown in a table below, labled *Optimums: (VMG)*. This shows the best angle
and sail to use while sailing upwind or downwind, as well as displaying the *Velocity Made Good*.

This information is also shown in graphical form on an interactive *Polar Chart*.

#### **Polar chart**

The polar chart plots the boat speed expected, while using each selected sail, at the various relative wind angles given the selected wind speed.
When the user hovers over a point on the graph, the wind angle, boat speed and sail type is displayed in a popup.

The user inputted wind angle is shown on the graph as a yellow dash-dotted line.
The optimum upwind and downwind sailing angles are shown on the graph by the red dotted lines.

Each sail, as well as the inputted wind angle, can be toggled on and off on the graph by clicking the legend.
The user can download a png image of the polar graph by clicking the camera icon at the top right of the plot.

A new tab showing just the polar chart can be opened by clicking on the button below the sailing information table or by folowing the
*Polar Chart* link in the navigation menu.

#### **Location based input**

Clicking on the *Location Based* dropdown in the nav bar allows the user to retrieve the current wind conditions for their location,
which is then inputted into the sailing information and polar chart.

The user can choose to use either the traditional *degrees, minuites and seconds* or *decimal degrees* as their position input type.

The user's current location can then be inputted by clicking the location arrow button.

The current wind is shown on a weather map. The map initially loads at a pre-set location, but updates when the users current location
is selected or form is submitted.

On desktop a wind picker is shown that displays the current wind direction and speed in that location, as well as the *picker's* coordinates.
On a mobile screen a pop-up showing the geographical coordinates is shown.

### **Background detail**

The output of this web app is a Polar Chart showing the boat speed expected at a given wind speed, at various wind angles for different sails.
It also displays a snippit of the plotted information in a table.

The webapp facilitates the input of two different types of information in order to produce the polar chart and sailing data table.

The first method is by using raw wind data inputted by the user.
This is done via forms found in the "index.html" and "output.html" pages.

The second method uses weather information gathered using the *Open Weather Map* api and user inputted geo-location data.
The geo-location data can be inputted into forms on the "dms.html" and "position.html" pages in degrees, minutes and seconds,
and on the "decimal.html" page in decimal degrees. On both pages the user can click a button to use their current location in the form.

On the pages using location based weather information a *Leaflet* map is displayed using the *Mapbox* api as a title layer and the *Windy* api
as an overlay to display graphical wind information. The Windy api allows the display of a *wind picker* on desktops, however, it is disabled on mobiles,
so a pop-up with location information is displayed instead.

Wind data from *Open Weather Map* is gathered and converted from m/s vector form to speed in kts and direction in degrees. The heading is then subtracted
from the wind direction to find the wind angle relative to the boat. This data is then used in the same way as the first method, to create a polar chart
and sailing data table.

The output page for "dms.html" and "decimal.html" is "position.html". This shows the polar chart and sailing data tables as well and the weather
map and a form to re-submit location data.

Located in the *static -> polars* are folders for each boat type. Within these folders are CSV files for each sail, with and without foils.
The CSV files contain data on the boat speed for wind speeds from 0-70kts at wind angles from 0-180 degrees.
These files were created using [*Toxcct's CSV Generator*](http://toxcct.free.fr/polars/generator.htm).

Originally I had planned to import these files to a SQLite database, however, when implemented alongside the other features of my web app,
the loading speed of the output pages was too slow. Instead, I used pandas.read_csv to access the rows and cells I required, which sped up
the processing considderably and also means that other boats can be added much more easily in future.

I used *Plotty* to display the speed v wind angle data for each sail on one polar graph. At first I saved this as a png image, however,
I changed this to an html file which is displayed in an iframe on the output pages. I decided to use an iframe and the html export
rather than an image file so that the graphs could be interactive and show pop-up lables, making them more user friendly and easier to interpret.

#### **Future development and improvements**

- Use sessions to ensure there is no conflict of information between different users
- Use forecasted weather to suggest sail choices over a route
- Users could create an account to save prefered data including location, routes and prefered boat
- Import geo-location data from *VR Dashboard* chrome extension
