#Imports
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo = False)

#Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect = True)

#Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def intro():
    """List all available app routes."""
    return(
        f"Welcome to sqlalchemy<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago).order_by(Measurement.date).all()
    session.close()

#Return the JSON representation of your dictionary.
    prcp_data = []
    for date, prcp in precipitation:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station]
    stations_list = session.query(*sel).all()
    session.close()

    all_stations = list(np.ravel(stations_list))

    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    year_temp = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_ago).all()

#Return a JSON list of temperature observations (TOBS) for the previous year.
    active_station = list(np.ravel(year_temp))
    return jsonify(active_station)


#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>") 
def start(start):
    start_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    calc_temps = list(np.ravel(start_results))
    return jsonify(calc_temps)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    between_temps = list(np.ravel(end_results))
    return jsonify(between_temps)

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)