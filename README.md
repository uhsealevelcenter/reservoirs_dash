
# Hawaii fresh water reservoirs dashboard

## Overall goal: Rewrite UHSLC fresh water reservoir dashboard using plotly dash:

*  A map that displays all the stations that we have for reservoirs - already implemented
* The data for each station containing names, station locations, and info is hosted in csv file here (one row per station): 
  [https://uhslc.soest.hawaii.edu/komar/stations.csv](https://uhslc.soest.hawaii.edu/komar/stations.csv)
* The current code already loads this CSV file
* The timeseries data for each station is located here:
  [https://uhslc.soest.hawaii.edu/reservoir/<station_id>.csv](https://uhslc.soest.hawaii.edu/reservoir/EDD00214.csv)
  Where <station_id> can be any of the station ids listed in the id column in the stations.csv file mentioned above (e.g. Waita station has id EDD00214). That way we can 'map' the station id to the timeseries data. In other words, the timeseries data for each station is located at the URL that is constructed by appending the station id to the base URL ([https://uhslc.soest.hawaii.edu/reservoir/](https://uhslc.soest.hawaii.edu/reservoir/)) so we can dynamically load the timeseries data for each station. 
* The desired behavior (just as the current JavaScript website functions) is as following:
    * Clicking on a station should create/update new plotly graph showing the water level and battery level data for each station
    * Have a table that lists all the stations (similar to the way it is done now, it does not have to look the same) so the map and the graph update based on what we click in the table. For example, if we select a station in the table, the map will pan to that station.
    * The marker for the currently selected station should be bigger/different color to indicate which station is selected (this functionality is not there in the JavaScript website)
    * There should also be a dropdown menu (as there currently is) that contains station id, dlnrid (dlnrid column in stations.csv) and station name
* Every station has to have its own URL so that we can link directly to a station (the example JavaScript website has this functionality)
* There needs to be a button that converts time from GMT to HST datetime (Hawaii Standard Time). The datetime is in date column in each of <station_id>.csv files and is GMT timezone by default in ISO format (yyyy-MM-dd'T'HH:mm:ss)
* Three buttons to show last 2 days, 1 week and 6 weeks of data
* A pop up that shows the disclaimer (the way it is implemented right now) after clicking Accept, the disclaimer should never show up again after reloading the page
