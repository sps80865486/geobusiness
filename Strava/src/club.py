'''
Created on 3 feb. 2019

@author: Sergio
'''

import logging
import geojson
from geojson import Feature, FeatureCollection, dump

from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import SQLClient
  

from flask import Flask, render_template, url_for, request
from stravalib import Client
from utils import utils

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

app = Flask(__name__)

@app.route("/")
def login():
    c = Client()
    url = c.authorization_url(client_id='30922',
                              redirect_uri=url_for('.logged_in', _external=True),
                              approval_prompt='auto')
    
    #Showing the login page
    return render_template('login.html', authorize_url=url)


@app.route("/strava-oauth")
def logged_in():
    """
    Method called by Strava (redirect) that includes parameters.
    - state
    - code
    - error
    """
    error = request.args.get('error')
    state = request.args.get('state')
    if error:
        return render_template('login_error.html', error=error)
    else:

        #Requesting the authorization code to STRAVA
        code = request.args.get('code')
        client = Client()
        access_token = client.exchange_code_for_token(client_id='30922',
                                                      client_secret='2791ad32fb846e9f5b567f0a0deba5bb168fe533',
                                                      code=code)
        
        logger.info(access_token)
        extractDataClub(client)
        
        return render_template('segment_results.html', segmentsPara=[],
                               segmentsNort=[], segmentsCAM=[],
                               segmentsCAS=[])        
        

# This function extract the data segment for a specified bounds
def extractDataClub(client):
    
    logger.info("VAMOS")

    HIJOS_DEL_PUERTO = 274645
    
    activitiesClub = client.get_club_activities(274645,limit=20)
    logger.info(activitiesClub)
    distTotal = float(0.0)
    altTotal= float(0.0)
    int = 0
    for activity in activitiesClub:
        logger.info(activity.athlete.firstname + " " + str(activity.athlete.sex))
        #logger.info(activity)
        #logger.info(str(activity.guid) + " " + str(activity.name) + " " +
        #            str(activity.distance) + " " + str(activity.total_elevation_gain) + " " +
        #            str(activity.kilojoules))
        distTotal = distTotal + float(activity.distance)
        altTotal = altTotal + float(activity.total_elevation_gain)
        int = int + 1
        
    logger.info(int)        
    logger.info(distTotal)
    logger.info(altTotal)        
        
        
if __name__ == '__main__':
    app.run(debug=True)        