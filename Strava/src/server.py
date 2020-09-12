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
            
        #Defining segments area bounds
        bounds_CAM=[40.366,-4.385,41.197,-3.573]
        bounds_NORT=[40.494,-3.876,41.197,-3.573]
        bounds_PARACUELLOS=[40.499,-3.546,40.844,-3.364]
        bounds_CASAVIEJA=[40.185,-5.043,40.458,-4.475]


        eleListPara= extractData(client,bounds_PARACUELLOS)
        eleListNort= extractData(client,bounds_NORT)            
        eleListCAM = extractData(client,bounds_CAM)
        eleListCAS = extractData(client,bounds_CASAVIEJA)
        
        # Dump to carto db
        utils.dumpToCarto(eleListNort,'north')
        utils.dumpToCarto(eleListPara,'para')
        utils.dumpToCarto(eleListCAM,'cam')
        utils.dumpToCarto(eleListCAS,'cas')
        
        return render_template('segment_results.html', segmentsPara=eleListPara,
                               segmentsNort=eleListNort, segmentsCAM=eleListCAM,
                               segmentsCAS=eleListCAS)
    
# This function extract the data segment for a specified bounds
def extractData(client, bounds):

    #Extracting the segments list in area
    segmentsList = client.explore_segments(bounds, activity_type=None, min_cat=None, max_cat=None)

    #Iterating over the segments
    eleList = []
    carto = open("carto.geojson","w+")

    features = []

    for seg in segmentsList:
        strava_segment = client.get_segment(seg.id)
        leaderboard = client.get_segment_leaderboard(strava_segment.id, gender=None, age_group=None, weight_class=None,
                            following=None, club_id=None, timeframe='this_year', top_results_limit=None,
                            page=None, context_entries = None)
        leaderboard_today = client.get_segment_leaderboard(strava_segment.id, gender=None, age_group=None, weight_class=None,
                            following=None, club_id=None, timeframe='today', top_results_limit=None,
                            page=None, context_entries = None)
        

        #extractDataSegment(client,strava_segment.id,strava_segment.name)
        
        ele = (strava_segment.id,
                strava_segment.name,
                strava_segment.effort_count,
                strava_segment.athlete_count,
                strava_segment.distance,
                leaderboard.entry_count,
                leaderboard_today.entry_count,
                strava_segment.start_latlng[1],
                strava_segment.start_latlng[0])
        eleList.append(ele)

        start_point = geojson.Point((strava_segment.start_latlng[1],
                                  strava_segment.start_latlng[0]))                      

        #Output by points        
        if (start_point):
            features.append(Feature(geometry=start_point, properties={"name": strava_segment.name,
                                                                      "value": leaderboard.entry_count }))
   

    eleList.sort(key=takeSecond, reverse=True)

    #Storing features
    feature_collection = FeatureCollection(features)
    
    #Dump to file
    dump(feature_collection, carto)
    
    #Close file
    carto.close()
    
    return eleList

def extractDataSegment(client,segmentId,segmentName):
    
        #Payment required
        leaderboard_25_34 = client.get_segment_leaderboard(segmentId, gender=None, age_group='25_34', weight_class=None,
                            following=None, club_id=None, timeframe='this_year', top_results_limit=None,
                            page=None, context_entries = None)
        
        leaderboard_35_44 = client.get_segment_leaderboard(segmentId, gender=None, age_group='35_44', weight_class=None,
                            following=None, club_id=None, timeframe='this_year', top_results_limit=None,
                            page=None, context_entries = None)
        leaderboard_45_54 = client.get_segment_leaderboard(segmentId, gender=None, age_group='45_54', weight_class=None,
                            following=None, club_id=None, timeframe='this_year', top_results_limit=None,
                            page=None, context_entries = None)  
        leaderboard_55_64 = client.get_segment_leaderboard(segmentId, gender=None, age_group='55_64', weight_class=None,
                            following=None, club_id=None, timeframe='this_year', top_results_limit=None,
                            page=None, context_entries = None) 
        leaderboard_65_plus = client.get_segment_leaderboard(segmentId, gender=None, age_group='65_plus', weight_class=None,
                            following=None, club_id=None, timeframe='this_year', top_results_limit=None,
                            page=None, context_entries = None)        
        
        logger.info("Atletas: 0-24"  + leaderboard_25_34.entry_count + " 35-44:" + leaderboard_35_44.entry_count + \
                    " 45-54:" + leaderboard_45_54.entry_count + " 55-64:" + leaderboard_55_64.entry_count + \
                    " 65_plus:" + leaderboard_65_plus.entry_count)
                                                         
    
#This function returns the second element of a list, for sorting purposes
def takeSecond(elem):
    return elem[2]


if __name__ == '__main__':
    app.run(debug=True)
