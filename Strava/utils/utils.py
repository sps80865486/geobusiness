'''
Created on 2 feb. 2019

@author: Sergio
'''

import logging

from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import SQLClient
from datetime import date

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# This function dump the list to the CARTO database
def dumpToCarto(eleList,table_name):
    
    # I am using my CARTO account
    USERNAME="sps80865486"
    USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
    auth_client = APIKeyAuthClient(api_key="53bb19efc968a08f7bdc2c1ffc29c31659240b39", base_url=USR_BASE_URL)

    sql = SQLClient(auth_client)
  
    table_name = 'strava_segments_' + table_name
    for segment in eleList:
        try:
            query = "UPDATE {table} SET cartodb_id={id}, the_geom=ST_SetSRID(ST_MakePoint({long}, {lat}),4326), name='{name}', value={value}, date=now() WHERE cartodb_id={id}". \
            format(table=table_name,id=segment[0],long=segment[7],lat=segment[8],name=segment[1],value=segment[2])
            logger.info(query)
            sql.send(query)
        except CartoException as e:
            logger.error(e)