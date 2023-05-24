import urllib
import requests
import json
from requests import NullHandler, exceptions
from requests.exceptions import SSLError
import datetime
from time import gmtime, strftime

from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config

import sys
sys.path.insert(0, '/opt/loginsight/loginsight-detect-error')

import inputs
from inputs_infra import *
from  login_session import login
import search

from alert_infra import send_telegram, send_teams


LIMIT_LOG= 500  #overwrite the default value
JSONFILE = "/opt/loginsight/loginsight-detect-error/projecta/output_projecta_manually.json"

def sql_insert(projecta_applicationCode, projecta_action, projecta_errorcode, datetime, projecta_count_event):
    query = "INSERT INTO projecta_count_event(projecta_applicationCode, projecta_action, projecta_errorcode, datetime, projecta_count_event) " \
            "VALUES(%s,%s,%s,%s,%s)"
    try:
        print ("query is: ", query)
        db_config = read_db_config()
        conn = None
        conn = MySQLConnection(**db_config)
        # print (conn)
        cursor = conn.cursor()
        args = (str(projecta_applicationCode),str(projecta_action),projecta_errorcode, str(datetime), projecta_count_event)

        #sql_insert(projecta_applicationCode, projecta_action, projecta_errorcode, datetime, projecta_count_event)    
        cursor.execute(query, args)
        conn.commit()
    except Error as error:
        print ("Mysql: Having error !!")
        print(error)
    # finally:
        # cursor.close()
        # conn.close()

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

    # #write the response to draf file:
    # with open("draf_response.out", "w") as draffile:
    #     draffile.write(COUNT)
    #     draffile.close()      


    for log in response['results']:
        print ("log is", log)

        try:
            result_dics['projecta_applicationCode'] = log['ibadcmc7ozxc4ztdnexg64dtpbygyylul5qxa4dmnfrwc5djn5xgg33emu000000']
            projecta_applicationCode = result_dics['projecta_applicationCode']            
        except:
            print ("Warn: No value for projecta_applicationCode")

        try:
            result_dics['projecta_errorcode'] = log['ibadcmc7ozxc4ztdnexg64dtpbygyylul5sxe4tpojrw6zdf']
            projecta_errorcode = result_dics['projecta_errorcode'] 
        except:
            print ("Warn: No value for projecta_errorcode")            

        try:
            result_dics['projecta_action'] = log['ibadcmc7ozxc4ztdnexg64dtpbygyylul5qwg5djn5xa0000']
            projecta_action = result_dics['projecta_action']
        except:
            print ("Warn: No value for projecta_action")

        try:
            result_dics['projecta_duration'] = log['ibadcmc7ozxc4ztdnexg64dtpbygc5c7mr2xeylunfxw4000']
        except:
            print ("Warn: No value for projecta_duration")

        try:
            result_dics['projecta_count_event'] = log['COUNT(event)']
            projecta_count_event = result_dics['projecta_count_event']
        except:
            print ("No value for projecta_count_event")

        strftime("%Y-%m-%d %H:%M:%S", gmtime())
        datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print("Current Time =", datetime)

        sql_insert(projecta_applicationCode, projecta_action, projecta_errorcode, datetime, projecta_count_event)    


        # for field in "projecta_code_status", "projecta_bucketname", "projecta_duration", "projecta_operation", "projecta_owneruserid":
        #     content_pack = "vn.fci.ops"
        #     try:   
        #         print ("field is", field )
        #         print (content_pack + ':' + field)
        #         field_new = content_pack + ':' + field
        #         result_dics[field] = log[field_new]
        #     except:
        #         print ("Content Pack " + content_pack +  " : have not field : {} ", content_pack,field)
        print(result_dics)
        with open(JSONFILE, "a+") as file:
            file.write(json.dumps(result_dics))
            file.write (",")
            file.close()
    
def msg_when_exceptions(error):
    msg = "<strong> Exception</strong> \n" \
            "<pre><code> \n" \
            "{} \n" \
            "</code></pre>". format(str(error))
    return msg

def main():

    sessionId=login(SERVER)
    if sessionId == False:
        print ("Error: Login fail")    
    else:        
        # print ("sessionId is: ", sessionId)        
        analyze(TEST_URL_XPLAT_HS_HTTP,sessionId,CHAT_ID_INFRA_NORMAL, trouble_link_TEXT_HTTP_EXCEPTION, mode="maintain", projectname="XPLAT-SG", alertname="5xx")        
        # analyze(TEST_URL_XPLAT_HS_HTTP_Duration_time,sessionId,CHAT_ID_INFRA_NORMAL, trouble_link_TEXT_HTTP_EXCEPTION, mode="maintain", projectname="XPLAT-SG", alertname="5xx")

if __name__ == "__main__":
    result_dics={} #this dictionary contains query results
    #renew output.json file

    file = open(JSONFILE, "a")
    file.seek(0)
    file.truncate()
    file.write ("[")
    file.close()
        
    main()
    print(result_dics) #finally print result query in dictionary format

    with open(JSONFILE, "a+") as file:
        # json.dumps(result_dics, file)
        file.write(json.dumps(result_dics))
        file.write ("]")
        file.close()
