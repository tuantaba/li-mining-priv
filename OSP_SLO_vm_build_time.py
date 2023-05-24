import urllib
import requests
import json
from requests import NullHandler, exceptions
from requests.exceptions import SSLError
import datetime

from inputs import *
from inputs_infra import *
from  login_session import login
import search

from alert_infra import send_telegram, send_teams

LIMIT_LOG= 500  #overwrite the default value
JSONFILE = "prom_exporter/output_osp.json"
def analyze(FULL_URL, sessionId, alertid, trouble_link, mode, projectname, alertname):    
    if ENV == "DEV":
        alertid = CHAT_ID_FOR_ADMIN

    result_dics = {}
    try:
        print ("quering.. ", FULL_URL)
        response = search.search(FULL_URL, sessionId)
    except exceptions as e:
        print ("Exception: ", e)
        msg =  msg_when_exceptions(e)
        send_telegram(msg, CHAT_ID_FOR_ADMIN)
        
    response = json.loads(response.text)
    print (response) 
    COUNT = response['numResults']
    print ("The number of matching data", COUNT)

    if COUNT == 0:
        print ("The query with no matched line, exit analyze() function...")
        return 1 
    print ("analyzing..") 

    for log in response['results']:
        print ("log is", log)

        try:
            result_dics['hostname'] = log['hostname']
        except:
            print ("Warn: No value for osp_operation")

        try:
            result_dics['osp_code_status'] = log['ibadcmc7ozxc4ztdnexg64dtnb2hi4c7mnxwizi0']
        except:
            print ("Warn: No value for osp_code_status")

        try:
            result_dics['osp_python_module'] = log['ibadcmc7ozxc4ztdnexg64dtob4xi2dpnzpw233eovwgk000']
        except:
            print ("Warn: No value for osp_operation")

        try:
            result_dics['osp_duration'] = log['ibadcmc7ozxc4ztdnexg64dtn5yhgx3bobyf65djnvsv64tfonyg63ttmu000000']
        except:
            print ("Warn: No value for osp_duration")

        try:
            result_dics['osp_count_event'] = log['COUNT(event)']
        except:
            print ("No value for osp_count_event")

        # print(result_dics)
        print (json.dumps(result_dics))
        
        with open(JSONFILE, "a+") as file:
            file.write(json.dumps(result_dics))
            file.write (",")
            file.close()

def main():

    sessionId=login(SERVER)
    if sessionId == False:
        print ("Error: Login fail")    
    else:        
        # print ("sessionId is: ", sessionId)        
        analyze(FULL_URL_SEARCH_OPS_RESPONSE,sessionId,CHAT_ID_INFRA_NORMAL, trouble_link_S3_HS_HTTP_5XX, mode="maintain", projectname="S3-SG", alertname="5xx")
        
        #Count  & sum, set via count number
        # analyze(URL_S3_HS_HTTP_DURAION,sessionId,CHAT_ID_INFRA_NORMAL, trouble_link_S3_HS_HTTP_5XX, mode="maintain", projectname="S3-SG", alertname="5xx")
        # analyze(TEST_URL_S3_HS_HTTP_5XX,sessionId,CHAT_ID_INFRA_NORMAL, trouble_link_S3_HS_HTTP_5XX, mode="maintain", projectname="S3-SG", alertname="5xx")
        # analyze(TEST_URL_S3_HS_HTTP,sessionId,CHAT_ID_INFRA_IMPORTANCE, trouble_link_S3_HS_HTTP_5XX, mode="maintain", projectname="S3-FOS", alertname="5xx")

if __name__ == "__main__":
    result_dics={} #this dictionary contains query results
    #renew output.json file
    file = open(JSONFILE, "a")
    file.seek(0)
    file.truncate()
    file.write ("[")
    file.close()  

    main()

    with open(JSONFILE, "a+") as file:
        # json.dumps(result_dics, file)
        file.write(json.dumps(result_dics))
        file.write ("]")
        file.close()