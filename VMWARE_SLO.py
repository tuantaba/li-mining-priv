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

LIMIT_LOG= 5000  #overwrite the default value
JSONFILE = "prom_exporter/output_vmware.json"

def analyze_event(FULL_URL, sessionId, field_name):    
    if ENV == "DEV":
        alertid = CHAT_ID_FOR_ADMIN

    result_dics = {}
    try:
        print ("quering.. ", FULL_URL)
        response = search.search(FULL_URL, sessionId)
        print (response)
    except exceptions as e:
        print ("Exception: ", e)
        msg =  msg_when_exceptions(e)
        send_telegram(msg, CHAT_ID_FOR_ADMIN)
    
    print (response) 
    response = json.loads(response.text)
    print (response) 
    COUNT = response['numResults']
    print ("The number of matching data", COUNT)
    # if COUNT == 0:
    #     print ("The query with no matched line, exit analyze() function...")
    #     return 1 
    # print ("analyzing..") 

    # for log in response['results']:
    #     print ("log is", log)
    #     try:
    #         result_dics['hostname'] = log['hostname']
    #     except:
    #         print ("Warn: No value for osp_operation")

    #     try:
    #         result_dics['osp_python_module'] = log['vn.fci.ops:python_module']
    #     except:
    #         print ("Warn: No value for osp_operation")

    #     try:
    #         result_dics['osp_vm_build_duration'] = log['vn.fci.ops:ops_vm_time_build']
    #     except:
    #         print ("Warn: No value for osp_vm_build_duration")

    result_dics[field_name] = COUNT
    print (json.dumps(result_dics))
    
    with open(JSONFILE, "a+") as file:
        file.write(json.dumps(result_dics))
        file.write (",")
        file.close()
    return COUNT    

def main():
    sessionId=login(SERVER_HANOI)
    if sessionId == False:
        print ("Error: Login fail")    
    else:        
        # print ("sessionId is: ", sessionId)        
        TOTAL_ACTION_EVENT = analyze_event(URL_VMWARE_ACTION_TOTAL_EVENT,sessionId, "TOTAL_ACTION_EVENT" )
        ERROR_ACTION_EVENT = analyze_event(URL_VMWARE_ACTION_ERROR_EVENT,sessionId, "ERROR_ACTION_EVENT" )

        print (TOTAL_ACTION_EVENT)
        print (ERROR_ACTION_EVENT)

        
        # analyze_event(FULL_URL_SEARCH_OPS_VM_RESPONSE,sessionId,CHAT_ID_INFRA_NORMAL, trouble_link_S3_HS_HTTP_5XX, mode="maintain", projectname="S3-SG", alertname="Build VM Time")

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