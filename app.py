#Imports
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect = True)

#Save reference to teh table
Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

app = Flask(__name__)

#Flask Routes
@app.route("/")
def intro():
    """List all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_year = dt.date(2017,8,23) - dt.timedelta(days = 365)
    recent_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > recent_year).order_by(Measurement.date).all()

    precipitation_data = []
    for i in precipitation:
        data = {}
        data['date'] = precipitation[0]
        data['prcp'] = preciptiation[1]
        precipitation_data.append(data)
    return jsonify(precipitation_data)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
    station_results = session.query(Stations.station).all()
    station_all = list(np.ravel(results))
    return jsonify(station_all)

#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
    tobs_results = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()
        list = []
        for i in tobs_results:
            dict = {}
            dict["station"] = tobs[0]
            dict["tobs"] = float(tobs[1])
            list.append(dict)
        return jsonify(list)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    start = datetime.strptime('2016-08-23', '%Y-%m-%d').date()
    start_results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs).\
        filter(Measurement.date >= start)
    start_tobs_list = []
    for i in start_results:
        dict = {}
        dict["TMIN"] = float(tobs[1])
        dict["TMAX"] = float(tobs[0])
        dict["TAVG"] = float(tobs[2])
        start_tobs_list.append(dict)
    return jsonify(start_tobs_list)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_end(start,end):
    start = datetime.strptime('2016-08-23', '%Y-%m-%d').date()
    end = datetime.strptime('2017-08-23', '%Y-%m-%d').date()
    end_results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs).\
        filter(Measurement.date >= start)
    start_end_tobs_list = []
    for i in start_end_tobs_list:
        dict = {}
        dict["TMIN"] = float(tobs[1])
        dict["TMAX"] = float(tobs[0])
        dict["TAVG"] = float(tobs[2])
        start_end_tobs_list.append(dict)
    return jsonify(start_end_tobs_list)

if __name__ == '__main__':
    app.run(debug=True)



