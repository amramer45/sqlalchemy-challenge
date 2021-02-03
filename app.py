#Imports
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
    return(
        f"Welcome to sqlalchemy<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_result = session.query(Measurement.date,Measurement.prcp).\
        order_by(Measurement.date).all()
    session.close()

#Return the JSON representation of your dictionary.
    prcp_data = []
    for date, prcp in prcp_result:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
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
    session = Session(engine)
    sel = [Measurement.date]
    last_date_str = session.query(*sel).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date_str[0], '%Y-%m-%d')
    year_ago = last_date - dt.timedelta(365)
    session.close()

    sel = [Measurement.stastion, func.count(Measurement.id)]
    active_station = session.query(*sel).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).all()
    most_active = active_station[0][0]

    sel = Measurement.date, Measurement.tobs
    tobs_info = session.query(*sel).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.date <= last_date).\
        filter(Measurement.date == most_active).\
        order_by(Measurement.date).all()
    session.close()

#Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_list = list(np.ravel(tobs_info))
    return jsonify(tobs_list)


#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start_date>")
def data_start_date(start_date):
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()

    session.close()

    start_tobs_list = []
    for i in start_results:
        start_dict = {}
        start_dict["TMIN"] = float(tobs[1])
        start_dict["TMAX"] = float(tobs[0])
        start_dict["TAVG"] = float(tobs[2])
        start_tobs_list.append(dict)
    
        return jsonify(start_tobs_list)

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date>/<end_date>")
def data_start_end_date(start_date, end_date):
    session = Session(engine)

    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    start_end_tobs_list = []
    for i in start_end_results:
        end_dict = {}
        end_dict["TMIN"] = float(tobs[1])
        end_dict["TMAX"] = float(tobs[0])
        end_dict["TAVG"] = float(tobs[2])
        start_end_tobs_list.append(dict)

        return jsonify(start_end_tobs_list)

if __name__ == '__main__':
    app.run(debug=True)