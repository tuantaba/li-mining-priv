import os
import time
import json

from requests import NullHandler, exceptions

# from requests import exceptions
from prometheus_client import start_http_server, Gauge, Enum, multiprocess, Histogram, Summary
# import time
# import requests

#Function for compatibility with Gunicorn
def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)

JSONFILE = "output_xplat.json"

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds
        _INF = float("inf")
        # self.xplat_duration = Histogram('xplat_duration', 'Duration Time in Sec', buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 4, 6, 8, 10, _INF))
        # self.xplat_duration = Histogram('xplat_duration', 'Duration Time in seconds', ['xplat_applicationCode', 'xplat_action'], buckets=(1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 80, 150 , 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 3000, 4000, _INF))
        self.xplat_duration = Summary('xplat_duration', 'Duration Time in seconds', ['xplat_applicationCode', 'xplat_action'])
        # self.xplat_duration = Summary('xplat_duration', 'Duration Time in seconds')
        self.xplat_count_event = Gauge("xplat_count_event", "S3 count HTTP request", ['nodename', 'xplat_errorcode', 'xplat_applicationCode', 'xplat_action'])
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
            nodename = "xplatcluster-sg"
            self.xplat_count_event.clear()
            for data_load in all_data_load:      
                try:
                    xplat_applicationCode = data_load["xplat_applicationCode"]
                except:
                    xplat_applicationCode = "unknow"
                try:
                    xplat_errorcode = data_load["xplat_errorcode"]
                except:
                    xplat_errorcode = "unknow"

                try:
                    xplat_action = data_load["xplat_action"]
                except:
                    xplat_action = "unknow"

                
                if "xplat_duration" in data_load: 
                    try:
                        #xplat_duration default  la Seconds
                        xplat_duration = float(data_load["xplat_duration"])
                        print ("xplat_duration is ", xplat_duration)                
                        self.xplat_duration.labels(xplat_applicationCode, xplat_action).observe(float(xplat_duration))
                        # self.xplat_duration.observe(float(xplat_duration))
                    except Exception as e:
                        print ("Error xplat_duration is:  ", e)                        
                elif "xplat_duration" not in data_load :                    
                    try:
                        xplat_count_event = data_load["xplat_count_event"]
                        self.xplat_count_event.labels(nodename, xplat_errorcode, xplat_applicationCode, xplat_action).set(xplat_count_event)
                    except Exception as e:
                        print ("Error xplat_count_event is:  ", e)
        except:
            print ("Error: JSONFILE can not to read" )
                
def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "86400"))  #setting to 12h  # need to set to 60s
    exporter_port = int(os.getenv("EXPORTER_PORT", "9882"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port, addr='172.17.0.1')
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
