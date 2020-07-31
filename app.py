#import dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Add your own start date to the end of the below route to query specific temp data (format: YYYY-MM-DD):<br/>"
        f"/api/v1.0/<br/>"
        f"OR<br/>"
        f"Add your own start and end dates to the end of the below route to query specific temp data (format: YYYY-MM-DD/YYYY-MM-DD):<br/>"
        f"/api/v1.0/<br/>"
        f"<br/>"
        f"Examples:<br/>"
        f"/api/v1.0/2016-06-04<br/>"
        f"/api/v1.0/2016-06-04/2017-03-02"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value (based on part 1 of HW)
#Design a query to retrieve the last 12 months of precipitation data.
@app.route("/api/v1.0/precipitation")
def precip():
    """Return a list of precipitation data over last last year"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #latest data point date:
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # source: https://stackoverflow.com/questions/23324266/converting-string-to-date-object-without-time-info
    #Create datetime object and then convert to date object
    last_date_convert = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_date_convert = last_date_convert.date()

    #calculating date 1 year before the last data point (not hardcoding, in case database changes):
    prev_yr_date = (last_date_convert- dt.timedelta(days = 365))

    # Perform a query to retrieve the data and precipitation scores for last year of data
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_yr_date).all()

    #close session
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation data
    precip_info = []

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    for row in prcp_data:
        precipitation_dict = {}
        precipitation_dict[row[0]] = row[1]
        precip_info.append(precipitation_dict)

    #jsonify results and return
    return jsonify(precip_info)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station names"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    active_stations = session.query(Measurement.station).group_by(Measurement.station).all()

    #close sessions
    session.close()

    # Convert list of tuples into normal list
    all_stations = [station[0] for station in active_stations]

    #jsonify results and return
    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def temp():
    """Return a list of temp data over last last year from most active station"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #latest data point date:
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # source: https://stackoverflow.com/questions/23324266/converting-string-to-date-object-without-time-info
    #Create datetime object and then convert to date object
    last_date_convert = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_date_convert = last_date_convert.date()

    #calculating date 1 year before the last data point (not hardcoding, in case database changes):
    prev_yr_date = (last_date_convert - dt.timedelta(days = 365))

    #find most active station by finding station with the most temp observations
    active_stations = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
            order_by(func.count(Measurement.tobs).desc()).all()

    most_active_station = active_stations[0][0]

    # Perform a query to retrieve the temp over last yr from most active station
    temp_data = session.query(Measurement.date, Measurement.tobs).\
             filter(Measurement.date >= prev_yr_date).\
             filter(Measurement.station == most_active_station).all()

    #close session
    session.close()

    # Create a dictionary from the row data and append to a list of temperature data
    temp_info = []

    #Convert the query results to a dictionary using date as the key and temp as the value.
    for row in temp_data:
        temperature_dict = {}
        temperature_dict[row[0]] = row[1]
        temp_info.append(temperature_dict)

    return jsonify(temp_info)

# #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Fetch the temp data that matches
       the path variable supplied by the user, or a 404 if not."""

    #make sure the date format is correct
    try:

        #convert input to a date
        start_date_convert = dt.datetime.strptime(start, '%Y-%m-%d')
        query_date_start = start_date_convert.date()

    #if date format is wrong
    except ValueError:
        return jsonify({"error": "Date format incorrect"}), 404

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #find first date in the database:
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()

    # source: https://stackoverflow.com/questions/23324266/converting-string-to-date-object-without-time-info
    #Create datetime object and then convert to date object
    first_date_convert = dt.datetime.strptime(first_date[0], '%Y-%m-%d')
    first_date_convert = first_date_convert.date()

    #find last date in the database:
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # source: https://stackoverflow.com/questions/23324266/converting-string-to-date-object-without-time-info
    #Create datetime object and then convert to date object
    last_date_convert = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_date_convert = last_date_convert.date()

    #determine if user date is within database range
    if (query_date_start < first_date_convert) | (query_date_start > last_date_convert) :
         #close session
        session.close()
        #return error message
        return jsonify({"error": "Date not found."}), 404
    
    else:

        #lowest temp recorded for most active station
        lowest_temp = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.date >= query_date_start).all()

        #highest temp recorded for most active station
        highest_temp = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.date >= query_date_start).all()

        #average temp recorded for most active station
        average_temp = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.date >= query_date_start).all()

        #close session
        session.close()

        #add results to a dictionary
        temp_info_dict = {
                        'TMax':highest_temp[0][0],
                        'TMin':lowest_temp[0][0],
                        'TAvg':round(average_temp[0][0],2)
                        }

        #jsonify dictionary result and return
        return jsonify(temp_info_dict)

#When given the start and the end date, calculate the TMIN, TAVG, 
# and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end (start, end):
    """Fetch the temp data that matches
       the path variable supplied by the user, or a 404 if not."""

    #make sure the date format is correct
    try:
        #convert inputs to dates
        #start date
        start_date_convert = dt.datetime.strptime(start, '%Y-%m-%d')
        query_date_start = start_date_convert.date()
   
        #end date
        end_date_convert = dt.datetime.strptime(end, '%Y-%m-%d')
        query_date_end = end_date_convert.date()

    #if date format is wrong
    except ValueError:
        return jsonify({"error": "Date format incorrect"}), 404

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #find first date in the database:
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()

    # source: https://stackoverflow.com/questions/23324266/converting-string-to-date-object-without-time-info
    #Create datetime object and then convert to date object
    first_date_convert = dt.datetime.strptime(first_date[0], '%Y-%m-%d')
    first_date_convert = first_date_convert.date()

    #find last date in the database:
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # source: https://stackoverflow.com/questions/23324266/converting-string-to-date-object-without-time-info
    #Create datetime object and then convert to date object
    last_date_convert = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_date_convert = last_date_convert.date()

    #determine if user date is within database range
    if (query_date_start < first_date_convert) | (query_date_start > last_date_convert) |(query_date_end < first_date_convert) | (query_date_end > last_date_convert):
        #close session
        session.close()
        #return error message
        return jsonify({"error": "Date not found."}), 404
        
    else:
        
        #lowest temp recorded for most active station
        lowest_temp = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.date >= query_date_start).\
                filter(Measurement.date<=query_date_end).all()

        #highest temp recorded for most active station
        highest_temp = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.date >= query_date_start).\
                filter(Measurement.date<=query_date_end).all()

        #average temp recorded for most active station
        average_temp = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.date >= query_date_start).\
                filter(Measurement.date<=query_date_end).all()

        #close session
        session.close()

        #add results to a dictionary
        temp_info_dict = {
                        'TMax':highest_temp[0][0],
                        'TMin':lowest_temp[0][0],
                        'TAvg':round(average_temp[0][0],2)
                        }

        #jsonify dictionary result and return
        return jsonify(temp_info_dict)

if __name__ == '__main__':
    app.run(debug=True)