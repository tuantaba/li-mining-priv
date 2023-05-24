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

JSONFILE = "output_AL.json"

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds
        self.AS_count_event = Gauge("AS_count_event", "AS count HTTP request", ['nodename', 'AS_code_status'])
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
            nodename = "AScluster-sg"
            for data_load in all_data_load:      
                try:
                    AS_code_status = data_load["AS_code_status"]
                except:
                    AS_code_status = "unknow"
                
                if "AS_count_event" in data_load:              
                    try:
                        AS_count_event = data_load["AS_count_event"]
                        print (AS_count_event)
                        self.AS_count_event.labels(nodename, AS_code_status).inc(AS_count_event)
                    except Exception as e:
                        print ("Error AS_count_event is:  ", e)
        except:
            print ("Error: JSONFILE can not to read" )
                
def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAS_SECONDS", "60"))  #set to 60s
    exporter_port = int(os.getenv("EXPORTER_PORT", "9889"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port, addr='172.17.0.1')
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()