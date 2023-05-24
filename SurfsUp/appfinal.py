# Import the dependencies.
import numpy as np
import datetime as dt 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func , MetaData

from flask import Flask,jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base= automap_base()
# metadata = MetaData()

# # reflect the table
Base.prepare(autoload_with = engine)
# metadata.reflect(engine, only=['measurement','station'])
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.measurement
# Base = automap_base(metadata=metadata)
# Base.prepare()
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List of all available routes"""
    return(f"Avalable Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br>")


@app.route("/api/v1.0/precipitation")
def percipitation():
    """Query last 12 months of percipitation data"""
    session = Session(engine)
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    columns = (Measurement.date,Measurement.prcp)
    prcp_data = session.query(*columns).filter(Measurement.date>= last_year).all()

    session.close()

    all_prcp = []
    for date,prcp in prcp_data:
        prcp_dict = {}
        prcp_dict[date]=prcp
        all_prcp.append(prcp_dict)
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """return a JSON list of stations from the dataset """

    session = Session(engine)

    stations  = session.query(Station.station,Station.id).all()

    session.close()

    all_stations = []
    for id, station in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"]= station
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """query the dates and temperature observations of the most active astiaon for the previous year of data"""
    """return a JSON list of temperature observations for the previous year"""
    session = Session(engine)

    most_active = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_id = most_active[0]
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    last_year_station =session.query(Measurement.date,Measurement.tobs).filter(Measurement.station== most_active_id).\
    filter(Measurement.date> last_year).all()

    session.close()

    all_tobs = []
    for tobs, date in last_year_station:
        tobs_dict = {}
        tobs_dict["tobs"]= tobs
        tobs_dict["date"]= date
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range"""
    session = Session(engine)
    stats= session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date <= start).all()
    session.close()

    start_tobs = []
    for TMIN,TAVG, TMAX in stats:
        start_dict = {}
        start_dict["TMIN"]= TMAX 
        start_dict["TAVG"]= TMIN
        start_dict["TMAX"]= TMAX
        start_tobs.append(start_dict)
    return jsonify(start_tobs)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range"""
    session = Session(engine)
    stats_1= session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date <= end).all()
      
    session.close()

    end_tobs = []
    for TMIN,TAVG,TMAX in stats_1:
        end_dict = {}
        end_dict["TMIN"]= TMAX 
        end_dict["TAVG"]= TAVG
        end_dict["TMAX"]= TMAX
        end_tobs.append(end_dict)
    return jsonify(end_tobs)

if __name__ == '__main__':
    app.run(debug=True)
