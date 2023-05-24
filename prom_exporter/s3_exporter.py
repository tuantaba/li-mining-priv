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

JSONFILE = "output_s3.json"

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        # self.s3_code_status = Enum("s3_code_status", "S3 HTTP RETURN CODE", ['nodename', 's3_bucketname'])
        # self.s3_duration = Gauge("s3_duration", "Duration Time in MicroSec of S3", ['nodename', 's3_bucketname', 's3_owneruserid', 's3_code_status', 's3_operation'])
        _INF = float("inf")
        # self.s3_duration = Histogram('s3_duration', 'Duration Time in Sec', buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 4, 6, 8, 10, _INF))
        self.s3_duration = Histogram('s3_duration', 'Duration Time in miliseconds', buckets=(50, 100, 200, 500, 1000, 2000, 4000, 6000, 8000, 10000, _INF))
              
        # self.s3_http_responses_5xx_total = Gauge("s3_http_responses_5xx_total", "S3 Total 5xx request", ['nodename', 's3_bucketname', 's3_owneruserid', 's3_code_status'])
        self.s3_count_event = Gauge("s3_count_event", "S3 count HTTP request", ['nodename', 's3_bucketname', 's3_owneruserid', 's3_code_status', 's3_operation'])
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
            nodename = "s3cluster-sg"
            self.s3_count_event.clear()
            for data_load in all_data_load:      
                try:
                    s3_bucketname = data_load["s3_bucketname"]
                except:
                    s3_bucketname = "unknow"
                try:
                    s3_owneruserid = data_load["s3_owneruserid"]
                except:
                    s3_owneruserid = "unknow"
                try:
                    s3_code_status = data_load["s3_code_status"]
                except:
                    s3_code_status = "unknow"

                try:
                    s3_operation = data_load["s3_operation"]
                except:
                    s3_operation = "unknow"
                
                if "s3_duration" in data_load: 
                    try:
                        #Chia cho 1 trieu vi s3_duration default  la MicroSecond
                        #Chia cho 1000 = ms
                        s3_duration = float(data_load["s3_duration"]) / 1000
                        print ("s3_duration is ", s3_duration)
                        # self.s3_duration.labels(nodename, s3_bucketname, s3_owneruserid, s3_code_status, s3_operation).set(s3_duration)
                        self.s3_duration.observe(int(s3_duration))
                    except Exception as e:
                        print ("Error s3_duration is:  ", e)
                elif "s3_duration" not in data_load :                    
                    try:
                        s3_count_event = data_load["s3_count_event"]
                        self.s3_count_event.labels(nodename, s3_bucketname, s3_owneruserid, s3_code_status, s3_operation).inc(s3_count_event)
                    except Exception as e:
                        print ("Error s3_count_event is:  ", e)
        except:
            print ("Error: JSONFILE can not to read" )
                
def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "60"))  #set to 60s
    exporter_port = int(os.getenv("EXPORTER_PORT", "9879"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port, addr='172.17.0.1')
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()