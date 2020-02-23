import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/<start>')
def get_temp_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temp_output = []
    for min,avg,max in queryresult:
        temp_output_dict = {}
        temp_output_dict["Min"] = min
        temp_output_dict["Average"] = avg
        temp_output_dict["Max"] = max
        temp_output.append(temp_output_dict)

    return jsonify(temp_output)

@app.route('/api/v1.0/<start>/<end>')
def get_temp_start_end(start,end):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_output = []
    for min,avg,max in queryresult:
        temp_output_dict = {}
        temp_output_dict["Min"] = min
        temp_output_dict["Average"] = avg
        temp_output_dict["Max"] = max
        temp_output.append(temp_output_dict)

    return jsonify(temp_output)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latestdateobj = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(latestdateobj, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    select = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*select).filter(Measurement.date >= querydate).all()
    session.close()

    temp_output = []
    for date, tobs in queryresult:
        temp_output_dict = {}
        temp_output_dict["Date"] = date
        temp_output_dict["Tobs"] = tobs
        temp_output.append(temp_output_dict)

    return jsonify(temp_output)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    select = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*select).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    select = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*select).all()
    session.close()

    prec = []
    for date, prcp in queryresult:
        prec_dict = {}
        prec_dict["Date"] = date
        prec_dict["Precipitation"] = prcp
        prec.append(prec_dict)

    return jsonify(prec)

if __name__ == '__main__':
    app.run(debug=True)