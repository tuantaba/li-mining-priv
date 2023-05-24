import os
import time
import json

from requests import NullHandler, exceptions

# from requests import exceptions
from prometheus_client import start_http_server, Gauge, Enum, multiprocess, Histogram
# import time
# import requests

#Function for compatibility with Gunicorn
def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)

JSONFILE = "output_vmware.json"

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds
        _INF = float("inf")
        # self.vmware_duration = Histogram('vmware_duration', 'Duration Time in Sec', buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 4, 6, 8, 10, _INF))
        # self.vmware_duration = Histogram('vmware_duration', 'Duration Time in seconds', ['vmware_applicationCode', 'vmware_action'], buckets=(1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 80, 150 , 200, 300, 400, 500, 600, 700, 800, 900, 1000, _INF))
        self.vmware_count_event = Gauge("vmware_count_event", "VMware Count Event", ['nodename', 'vmware_event_type'])
        self.health = Enum("app_health", "Health", states=["healthy", "unhealthy"])

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        try: 
            with open(JSONFILE, 'r') as file:
                all_data_load = json.load(file)
            #for json
            nodename = "vmwarecluster"
            for data_load in all_data_load:      
                if "TOTAL_ACTION_EVENT" in data_load:                  
                    try:
                        TOTAL_ACTION_EVENT = data_load["TOTAL_ACTION_EVENT"]
                        self.vmware_count_event.labels(nodename, "TOTAL_ACTION_EVENT").inc(TOTAL_ACTION_EVENT)            
                    except Exception as e:
                        print ("Error vmware_count_event (label TOTAL_ACTION_EVENT) is:  ", e)                        
                elif "ERROR_ACTION_EVENT" in data_load:                  
                    try:
                        ERROR_ACTION_EVENT = data_load["ERROR_ACTION_EVENT"]
                        self.vmware_count_event.labels(nodename, "ERROR_ACTION_EVENT").inc(ERROR_ACTION_EVENT)                
                    except Exception as e:
                        print ("Error vmware_count_event (label ERROR_ACTION_EVENT) is:  ", e)
        except:
            print ("Error: JSONFILE can not to read" )
                
def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "3600"))  #set to 1h
    exporter_port = int(os.getenv("EXPORTER_PORT", "9883"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port, addr='172.17.0.1')
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()