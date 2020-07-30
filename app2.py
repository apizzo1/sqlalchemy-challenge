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
    #extract day, month, and year
    day = dt.date.strftime(last_date_convert,'%d')
    month = dt.date.strftime(last_date_convert,'%m')
    year = dt.date.strftime(last_date_convert,'%Y')

    #calculating date 1 year before the last data point (not hardcoding, in case database changes):
    prev_yr_date = dt.date(int(year), int(month), int(day)) - dt.timedelta(days = 365)

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
    #extract day, month, and year
    day = dt.date.strftime(last_date_convert,'%d')
    month = dt.date.strftime(last_date_convert,'%m')
    year = dt.date.strftime(last_date_convert,'%Y')

    #calculating date 1 year before the last data point (not hardcoding, in case database changes):
    prev_yr_date = dt.date(int(year), int(month), int(day)) - dt.timedelta(days = 365)

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

    #convert input to a date

    start_date_convert = dt.datetime.strptime(start, '%Y-%m-%d')
    start_date_convert = start_date_convert.date()
    start_day = dt.date.strftime(start_date_convert,'%d')
    start_month = dt.date.strftime(start_date_convert,'%m')
    start_year = dt.date.strftime(start_date_convert,'%Y')

    query_date_start = dt.date(int(start_year), int(start_month),int(start_day))

    data_start = dt.date(2010, 1,1)
    data_end = dt.date(2017, 8,23)

    #determine if user date is within database range
    if (query_date_start < data_start) | (query_date_start > data_end) :
        
        #return error message
        return jsonify({"error": "Date not found."}), 404
    
    else:

        session = Session(engine)
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

    #convert inputs to dates
    #start date
    start_date_convert = dt.datetime.strptime(start, '%Y-%m-%d')
    start_date_convert = start_date_convert.date()
    start_day = dt.date.strftime(start_date_convert,'%d')
    start_month = dt.date.strftime(start_date_convert,'%m')
    start_year = dt.date.strftime(start_date_convert,'%Y')
    #end date
    end_date_convert = dt.datetime.strptime(end, '%Y-%m-%d')
    end_date_convert = end_date_convert.date()
    end_day = dt.date.strftime(end_date_convert,'%d')
    end_month = dt.date.strftime(end_date_convert,'%m')
    end_year = dt.date.strftime(end_date_convert,'%Y')
    
    query_date_start = dt.date(int(start_year), int(start_month),int(start_day))
    query_date_end = dt.date(int(end_year), int(end_month),int(end_day))

    #set min and max dates from database
    data_start = dt.date(2010, 1,1)
    data_end = dt.date(2017, 8,23)

    #determine if user date is within database range
    if (query_date_start < data_start) | (query_date_start > data_end) |(query_date_end < data_start) | (query_date_end > data_end):
        return jsonify({"error": "Date not found."}), 404
    
    else:

        # Create our session (link) from Python to the DB
        session = Session(engine)
        
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