# Import Flask
from flask import Flask

# Set up dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import MetaData, Table
from datetime import datetime, timedelta 
from matplotlib import style
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create an app
app = Flask(__name__)

@app.route("/")
def home():
    print("I've received your request for 'Home' page.")
    return(
        f"Welcome to SQLAlchemy Step 2<br>"
        f"The available routes are:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Set up tuple
    max_date = max_date[0]

    # Calculate one year ago date
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)

    #Query data and precip
    precipitation_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert tuples to normal list
    precipitation_results_dict = dict(precipitation_results)

    return jsonify(precipitation_results_dict)

@app.route("/api/v1.0/stations")
def stations():
	# Query stations
	stations_results = (session.query(Measurement.station, 
    func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())

	# Convert to normal list
	stations_list = list(np.ravel(stations_results))

	return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
	
	# Query the last 12 months of precipitation data
	max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

	# Set up tuple
	max_date = max_date[0]

	# Calculate the date 1 year ago from today
	year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)

	# Query tobs
	tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

	# Convert to normal list
	tobs_list = list(tobs_results)

	return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
	
	start_results = session.query(Measurement.date, func.min(Measurement.tobs), 
    func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
	
	start_list = list(start_results)
	return jsonify(start_list)
	

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
	# Docstring
	
	startend_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), 
    func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
	dates_list = list(startend_dates)
	
	return jsonify(dates_list)

if __name__ == '__main__':
	app.run(debug=True)

