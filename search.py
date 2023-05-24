import urllib
import requests
import json
from requests import exceptions
from requests.exceptions import SSLError

# from inputs import *

# SERVER = "https://sgn09md01vli.inside.fptcloud.com"
# URI_LOGIN= "/api/v1/sessions"
# URI_CHECK_SESSION="/api/v1/sessions/current"


def search(FULL_URL, sessionId):        
    headers = {"Authorization": "Bearer " + sessionId ,\
            "Content-Type" : "application/json", \
            "Accept": "application/json"
        }
    try: 
        response = requests.get(url=FULL_URL, headers=headers,verify=False)

        # print (response.status_code)
        # print(r.json())
        # print(response.content)

        # json_data = json.loads(response.text)

        # COUNT = json_data['numResults']
        # print ("The number of matching data", COUNT)
    except exceptions as e:
        print ("search error ", e)
        response = {"error": e}

    return response
