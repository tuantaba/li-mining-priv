from inputs_infra import CHAT_ID_INFRA_IMPORTANCE
import urllib
import requests
import json
from requests import NullHandler, exceptions
from requests.exceptions import SSLError
import datetime

from inputs import *
from  login_session import login
import search

import alert

JSONFILE = "prom_exporter/output_osp1.json"

def analyze(FULL_URL, sessionId, alert_id_array, mode):
    try:
        print ("quering.. ", FULL_URL)
        response = search.search(FULL_URL, sessionId)
    except exceptions as e:
        print ("Exception: ", e)
        msg =  msg_when_exceptions(e)
        alert.send_telegram(msg, CHAT_ID_FOR_ADMIN)
        
    response = json.loads(response.text)
    print (response)
    
    COUNT = response['numResults']
    print ("The number of matching data", COUNT)

    if COUNT == 0:
        print ("The query with no matched line, exit analyze() function...")
        return 1 
    print ("analyzing..")
    alert_tag=False
    
    for log in response['results']:        
        hostname = log['hostname']
        Timestamp = log['timestampString']
        
        alert_tag=False  #Tag for alert, = True will alert!
        result_dics['hostname'] = hostname
        result_dics['Timestamp'] = Timestamp
        # try:
        #     Timestamp =  _Timestamp +  datetime.timedelta(hours=7)
        # except:
        #     Timestamp = _Timestamp

        text = log['text']
        try:
            filepath = log['filepath']  #ex: /var/log/kolla/cinder/cinder-wsgi.log"
            if filepath == "/var/log/kolla/fluentd/fluentd.log":
                alert_tag=True
        except:
            filepath = "null"        
        ops_service = filepath.split('/')[4]
        ops_subservice_2 = filepath.split('.')[0]
        ops_subservice =  ops_subservice_2.split('/')[5]
        msg_reason=""
        
        msg =  "  hostname: " + hostname + " \n"
        try:
            python_module = log['vn.fci.ops:python_module']
            result_dics['python_module'] = python_module
            msg = msg  + "  module: " + python_module + " \n"            
        except:
            python_module = "null"
            
        try:            
            log_level = log['vn.fci.ops:log_level']
            result_dics['log_level'] = log_level
            msg = msg  + "  log_level: " + log_level + " \n"
            if log_level == "error" or  log_level == "err" or log_level == "ERROR" or log_level == "ERR":
                msg_reason="log_level"
                alert_tag=True
        except:
            log_level = "null"   

        try:
            ops_rabbit_log_level = log['vn.fci.ops:ops_rabbit_log_level']
            result_dics['ops_rabbit_log_level'] = ops_rabbit_log_level            

            msg = msg  + "  rabbit_log_level: " + ops_rabbit_log_level + " \n"
            if ops_rabbit_log_level == "error" or  ops_rabbit_log_level == "err" or ops_rabbit_log_level == "ERROR" or ops_rabbit_log_level == "ERR":
                msg_reason="log_level"
                alert_tag=True
        except:
            ops_rabbit_log_level = "null"   

        try:
            http_code = log['vn.fci.ops:http_code']            
            result_dics['http_code'] = http_code          
            msg = msg  + "  http_code: " + http_code + " \n"
            if  int(http_code)  >= 500:
                alert_tag=True
                if msg_reason != "":
                    msg_reason = msg_reason + ", code 5xx"
                else:
                    msg_reason = msg_reason + "code 5xx"                    
            elif  int(http_code) >= 400:
                if msg_reason != "":
                    msg_reason = msg_reason + ", code 4xx"
                else:
                    msg_reason = msg_reason + "code 4xx"
            else:
                print ("return code ok")                
        except:
            http_code = "null"   

        try:
            http_path = log['vn.fci.ops:http_path']
            result_dics['http_path'] = http_path   
            msg = msg  + "  http_path: " + http_path + " \n"
        except:
            http_path = "null"

        try:
            ops_request_id = log['vn.fci.ops:ops_request_id']
            # msg = msg  + "    OPS_request_id: " + ops_request_id + " \n"
        except:
            ops_request_id = "null"

        try:
            ops_app_time_response = log['vn.fci.ops:ops_app_time_response']
            result_dics['ops_app_time_response'] = ops_app_time_response
            if ops_app_time_response >= OPS_RESPONSE_TIME_CRIT:
                alert_tag=True
                msg = msg  + " <strong> Critical Response: " + ops_app_time_response + "s </strong> \n"  

                if msg_reason != "":
                    msg_reason = msg_reason + ", response > " + OPS_RESPONSE_TIME_CRIT +"s"
                else:
                    msg_reason = msg_reason + "response > " + OPS_RESPONSE_TIME_CRIT +"s"
            elif  ops_app_time_response >= OPS_RESPONSE_TIME_WARN:
                alert_tag=True
                msg = msg  + " <strong> Warning Response: " + ops_app_time_response + "s </strong> \n"

                if msg_reason != "":
                    msg_reason = msg_reason + ", response > " + OPS_RESPONSE_TIME_WARN +"s"
                else:
                    msg_reason = msg_reason + "response > " + OPS_RESPONSE_TIME_WARN +"s"
            else:
                msg = msg  + "  Time Response: " + ops_app_time_response  + "s \n"              
        except:
            ops_app_time_response = "null"

#Time response for VM
#add ID VM for debug ?
        try:
            ops_vm_time_build = log['vn.fci.ops:ops_vm_time_build']
            result_dics['ops_vm_time_build'] = ops_vm_time_build
            msg = msg  + "  ops_vm_time_build: " + ops_vm_time_build + "s \n"

            if ops_vm_time_build >= threshold_ops_vm_time_build:
                alert_tag=True
                if msg_reason != "":
                    msg_reason = msg_reason + ", vm_time_build > " + threshold_ops_vm_time_build + "s"
                else:
                    msg_reason = msg_reason + "vm_time_build > " + threshold_ops_vm_time_build + "s"              
        except:
            ops_vm_time_build = "null"

        try:
            ops_vm_time_spawn = log['vn.fci.ops:ops_vm_time_spawn']
            result_dics['ops_vm_time_spawn'] = ops_vm_time_spawn
            msg = msg  + "  ops_vm_time_spawn: " + ops_vm_time_spawn + "s \n"
            if ops_vm_time_spawn >= threshold_ops_vm_time_spawn:
                alert_tag=True
                if msg_reason != "":
                    msg_reason = msg_reason + ", vm_time_spawn > " + threshold_ops_vm_time_spawn + "s"
                else:
                    msg_reason = msg_reason + "vm_time_spawn > " + threshold_ops_vm_time_spawn + "s"   
        except:
            ops_vm_time_spawn = "null"

        try:
            ops_vm_time_deallocate_network = log['vn.fci.ops:ops_vm_time_deallocate_network']
            result_dics['ops_vm_time_deallocate_network'] = ops_vm_time_deallocate_network
            msg = msg  + "  ops_vm_time_deallocate_network: " + ops_vm_time_deallocate_network  + "s \n"
            if ops_vm_time_deallocate_network >= threshold_ops_vm_time_deallocate_network:
                alert_tag=True
                if msg_reason != "":
                    msg_reason = msg_reason + ", vm_time_deallocate_network > " + threshold_ops_vm_time_deallocate_network + "s"
                else:
                    msg_reason = msg_reason + "vm_time_deallocate_network > " + threshold_ops_vm_time_deallocate_network + "s"   
        except:
            ops_vm_time_deallocate_network = "null"

        try:
            ops_vm_time_detach_volume = log['vn.fci.ops:ops_vm_time_detach_volume']
            result_dics['ops_vm_time_detach_volume'] = ops_vm_time_detach_volume
            msg = msg  + "  ops_vm_time_detach_volume: " + ops_vm_time_detach_volume  + "s \n"
            if ops_vm_time_detach_volume >= threshold_ops_vm_time_detach_volume:
                alert_tag=True
                if msg_reason != "":
                    msg_reason = msg_reason + ", vm_time_detach_volume > " + threshold_ops_vm_time_detach_volume + "s"
                else:
                    msg_reason = msg_reason + "vm_time_detach_volume > " + threshold_ops_vm_time_detach_volume + "s"   
        except:
            ops_vm_time_detach_volume = "null"

        with open(JSONFILE, "a+") as file:
            # json.dumps(result_dics, file)
            file.write(json.dumps(result_dics))
            file.write (",")
            file.close()            
#End Time response for VM

#Alert session
        if alert_tag == True:
            print ("Alert session: Have seen alerting")
            msg = msg  + "  Time: " + Timestamp + " \n"     
            text=fix_bug_send_telegram(text)
            msg = msg + "<pre><code> \n" +  text + "\n </code></pre> "   
        
            msg_header =  "<strong> [OPS event " +  msg_reason  +  "] " + ops_service + " : "  + ops_subservice + "</strong> \n"
            #Eg: [OPS vm_time_build > 30s] nova : nova-compute

            msg  =  msg_header +  msg
            print(msg)
                
            print (hostname)
            print (log_level)
            print (python_module)
            print (ops_app_time_response)
            print (http_code)
            print(ops_rabbit_log_level)

            try:
                print ("alert!")
                if mode == "release":
                    for alert_id in alert_id_array:                                             
                        print  ("alert_id_array is ", alert_id_array)
                        try:
                            alert.send_telegram(msg,str(alert_id))
                            print ("alert_id is: ", str(alert_id))
                            # alert.send_teams(msg, str(TEAMS_API_TEST))
                        except:
                            alert.send_telegram(msg, CHAT_ID_FOR_ADMIN)
                elif mode == "maintain":
                    alert.send_telegram(msg,CHAT_ID_FOR_ADMIN)
                    # alert.send_teams(msg, str(TEAMS_API_TEST))
                else:
                    alert.send_telegram(msg,CHAT_ID_FOR_ADMIN)
                    # alert.send_teams(msg, str(TEAMS_API_TEST))

            except exceptions as e:
                print  ("Error", e)
                msg =  msg_when_exceptions(e)
                alert.send_telegram(msg, CHAT_ID_FOR_ADMIN)
        else:
            print ("Alert session: Nothing to alert")
#End of Alert session            

def msg_when_exceptions(error):
    msg = "<strong> Exception</strong> \n" \
            "<pre><code> \n" \
            "{} \n" \
            "</code></pre>". format(str(error))
    return msg

def fix_bug_send_telegram(_string):
    _string=_string.replace("<", "tag;")
    _string=_string.replace(">", "tag;")
    _string=_string.replace("&", "tag;")
    _string=_string.replace("#", "tag;")
    return _string

def format_msg_for_openstack(arg1, arg2, arg3, arg4, arg5, arg6):
    msg = "<strong>{}</strong> \n <br>" \
            "     Hostname: {}\n" \
            "     Module: {}\n" \
            "     Log_level: {} \n" \
            "     Time: {} \n" \
            "<pre><code> \n" \
            "{}\n" \
            "</code></pre>". format(arg1,arg2,arg3,arg4,arg5,arg6)
    return msg

def format_msg_for_http(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    msg = "<p><strong>{}</strong> \n <br>"  \
            "     Hostname: {}\n" \
            "     http_code: {}\n" \
            "     http_method: {} \n" \
            "     http_url: {} \n" \
            "     Time: {} \n" \
            "<pre><code> \n" \
            "{}\n</p>" \
            "</code></pre>". format(arg1,arg2,arg3,arg4,arg5,arg6,arg7)
    return msg

def format_msg_for_system_local(arg1, arg2, arg3, arg4, arg5):
    msg = "<strong>System: {}</strong> \n <br>" \
            "     Hostname: {}\n" \
            "     log_level: {} \n" \
            "     Time: {} \n" \
            "<pre><code> \n" \
            "{}\n" \
            "</code></pre>". format(arg1,arg2,arg3,arg4,arg5)
    return msg

def main():
    sessionId=login(SERVER)
    if sessionId == False:
        print ("Error: Login fail")    
    else:
        # analyze(URL_HTTP_4XX,sessionId,[CHAT_ID], mode="maintain")        
        # # print ("sessionId is: ", sessionId)
        analyze(URL_APP_RESPONSE_HIGHT,sessionId,[CHAT_ID], mode="release")
        # analyze(URL_TEXT_IMPORTANCE,sessionId, mode="release")
        analyze(URL_ops_vm_time_build,sessionId,[CHAT_ID], mode="release")
        analyze(URL_HTTP_5XX,sessionId,[CHAT_ID_INFRA_NORMAL], mode="release")

        analyze(URL_LOG_LEVEL_ERROR,sessionId,[CHAT_ID], mode="release")
        analyze(URL_OVN_ELECTED_LEADER,sessionId,[CHAT_ID], mode="release")
        # analyze(URL_HTTP_5XX_BARBICAN,sessionId,[CHAT_ID], mode="release")
        analyze(URL_MASAKARI,sessionId,[CHAT_ID], mode="release")
        # analyze(URL_HTTP_4XX,sessionId, mode="maintain")
        analyze(URL_RABBIT_LOG_LEVEL_ERROR,sessionId,[CHAT_ID], mode="release")        
        # analyze(URL_ops_vm_time_spawn,sessionId,[CHAT_ID], mode="maintain")
        # analyze(URL_ops_vm_time_detach_volume,sessionId,[CHAT_ID], mode="maintain")
        # analyze(URL_ops_vm_time_deallocate_network,sessionId,[CHAT_ID], mode="maintain")
        # analyze(URL_LOG_LEVEL_ERROR_ONLY_MONASCA,sessionId,[CHAT_ID], mode="release")
        # analyze(URL_HTTP_5XX_ONLY_MONASCA,sessionId,[CHAT_ID], mode="release")
        analyze(URL_RABBIT_LOG_LEVEL_ERROR,sessionId,[CHAT_ID], mode="release")
        analyze(URL_MQ_OVERFUL_MEM,sessionId,[CHAT_ID_INFRA_IMPORTANCE_2], mode="release")
        analyze(SEARCH_CLOUD_GUARD,sessionId,[CHAT_ID_CLOUD_GUARD], mode="release")
            
if __name__ == "__main__":
    result_dics={} #this dictionary contains query results
    #renew output.json file

    if ENV == "DEV":
        CHAT_ID = CHAT_ID_FOR_ADMIN
        CHAT_ID_INFRA_NORMAL = CHAT_ID_FOR_ADMIN
        CHAT_ID_INFRA_IMPORTANCE = CHAT_ID_FOR_ADMIN
    main()
    print(result_dics) #finally print result query in dictionary format
    file = open(JSONFILE, "a")
    file.seek(0)
    file.truncate()
    file.write ("[")
    file.close()

    with open(JSONFILE, "a+") as file:
        # json.dumps(result_dics, file)
        file.write(json.dumps(result_dics))
        file.write ("]")
        file.close() 
