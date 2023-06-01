from pandas import read_excel, DataFrame
from string import Template

from pandas.core.indexes.base import Index

alert_sheet = 'Alert_for_FIM'
file_name = 'FIM.xls'
OUTPUT_FILE_TCP = 'tcp_output.json'
OUTPUT_FILE_PING = 'ping_output.json'
OUTPUT_FILE_HTTP = 'http_output.json'
OUTPUT_FILE_HTTPS = 'https_output.json'


ignored_values = ["1.1.1.1:6080"]

def mining_xls(Protocol, OUTPUT_FILE):
    data = read_excel(file_name, sheet_name=alert_sheet, usecols=("A,B,C"))
    # data_tcp = data.query('Protocol == "TCP" & Service != "Gnocchi"')
    if Protocol == "TCP":        
        data_tcp = data.query('Protocol == "TCP"')
    elif Protocol == "PING":
        data_tcp = data.query('Protocol == "PING"')
    elif Protocol == "HTTP":
        data_tcp = data.query('Protocol == "HTTP"')
    elif Protocol == "HTTPS":
        data_tcp = data.query('Protocol == "HTTPS"')

    data_tcp = data_tcp.fillna(method='ffill', axis=0)

    file = open(OUTPUT_FILE, "a")
    file.seek(0)
    file.truncate()
    file.write("[")
    file.close()

    for i, row in  enumerate(data_tcp.index):
        print (data_tcp['Service'][row],data_tcp['Protocol'][row] , data_tcp['IP[:port]'][row] )
        service = data_tcp['Service'][row]
        protocol = data_tcp['Protocol'][row]
        ipport = data_tcp['IP[:port]'][row]

        if (ipport not in ignored_values and ":22" not in ipport ):
            t =  Template('{ \n \
                "targets": [   \n\
                "$ipport"   \n\
                ],  \n\
                "labels": {  \n\
                "service": "$service",   \n\
                "protocol": "$protocol"   \n\
                }  \n\
            }   \n\
            ')
            json_text =t.substitute(service=service,protocol=protocol,ipport=ipport )
            print (json_text)
            
            #write to json file 
            with open(OUTPUT_FILE, "a+") as file:
                file.write(json_text)
                if (i != len(data_tcp.index)-1): #if is last element
                # print ("last element is")   
                    file.write(",")
                file.close()
            
            # with open('check_tcp.txt', "a+") as filetxt:
            #     filetxt.write(ipport)
            #     filetxt.write("\n")
            #     filetxt.close()
            
    with open(OUTPUT_FILE, "a+") as file:
        file.write("]")
        file.close()

mining_xls("TCP", OUTPUT_FILE_TCP)
mining_xls("PING", OUTPUT_FILE_PING)
mining_xls("HTTP", OUTPUT_FILE_HTTP)
mining_xls("HTTPS", OUTPUT_FILE_HTTPS)
data = read_excel(file_name, sheet_name=alert_sheet, usecols=("A,B,C"))
data_tcp = data.query('Protocol == "TCP" & Service != "Gnocchi"')
data_tcp = data_tcp.fillna(method='ffill', axis=0)

file = open('check_tcp_test.json', "a")
file.seek(0)
file.truncate()
file.write("[")
file.close()

for i, row in  enumerate(data_tcp.index):
    print (data_tcp['Service'][row],data_tcp['Protocol'][row] , data_tcp['IP[:port]'][row] )
    service = data_tcp['Service'][row]
    protocol = data_tcp['Protocol'][row]
    ipport = data_tcp['IP[:port]'][row]

    if (ipport not in ignored_values and ":22" not in ipport ):
        t =  Template('{ \n \
            "targets": [   \n\
            "$ipport"   \n\
            ],  \n\
            "labels": {  \n\
            "service": "$service",   \n\
            "protocol": "$protocol"   \n\
            }  \n\
        }   \n\
        ')
        json_text =t.substitute(service=service,protocol=protocol,ipport=ipport )
        print (json_text)
        
        #write to json file 
        with open('check_tcp_test.json', "a+") as file:
            file.write(json_text)
            if (i != len(data_tcp.index)-1): #if is last element
            # print ("last element is")   
                file.write(",")
            file.close()
        
        with open('check_tcp.txt', "a+") as filetxt:
            filetxt.write(ipport)
            filetxt.write("\n")
            filetxt.close()
        
with open('check_tcp_test.json', "a+") as file:
    file.write("]")
    file.close()
