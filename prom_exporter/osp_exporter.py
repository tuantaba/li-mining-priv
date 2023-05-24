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

JSONFILE = "output_osp.json"

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        # self.s3_code_status = Enum("s3_code_status", "OSP HTTP RETURN CODE", ['nodename', 's3_bucketname'])
        # self.osp_duration = Gauge("osp_duration", "Duration Time in MicroSec of OSP", ['nodename', 's3_bucketname', 's3_owneruserid', 's3_code_status', 's3_operation'])
        _INF = float("inf")
        self.osp_duration = Histogram('osp_duration', 'Duration Time in Sec', buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 4, 6, 8, 10, _INF))
        self.osp_vm_build_duration = Histogram('osp_vm_build_duration', 'Duration Time in Sec', buckets=(10, 20, 30, 40, 60, 80, 100, 120, 150, 200, 300, 500, _INF))
              
        # self.s3_http_responses_5xx_total = Gauge("s3_http_responses_5xx_total", "OSP Total 5xx request", ['nodename', 's3_bucketname', 's3_owneruserid', 's3_code_status'])
        self.osp_count_event = Gauge("osp_count_event", "OSP count HTTP request", ['hostname', 'osp_python_module', 'osp_code_status', 'service_exporter'])
        # self.osp_vm_build_duration = Gauge("osp_vm_build_duration", "OSP VM Build Time", ['hostname', 'osp_python_module', 'service_exporter'])
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
            service_exporter = "ospcluster-sg"
            for data_load in all_data_load:      
                try:
                    osp_python_module = data_load["osp_python_module"]
                except:
                    osp_python_module = "unknow"
                try:
                    hostname = data_load["hostname"]
                except:
                    hostname = "unknow"
                try:
                    osp_code_status = data_load["osp_code_status"]
                except:
                    osp_code_status = "unknow"

                print (osp_python_module)
                print (hostname)
                print (osp_code_status)
                                    
                if "osp_duration" in data_load: 
                    try:
                        osp_duration = float(data_load["osp_duration"]) 
                        print ("osp_duration is ", osp_duration)
                        # self.osp_duration.labels(service_exporter, hostname, osp_python_module, osp_code_status).set(osp_duration)
                        self.osp_duration.observe(osp_duration)
                    except Exception as e:
                        print ("Error osp_duration is:  ", e)
                elif "osp_vm_build_duration"  in data_load :
                    try:
                        osp_vm_build_duration = float(data_load["osp_vm_build_duration"]) 
                        print ("osp_vm_build_duration is ", osp_vm_build_duration)
                        self.osp_vm_build_duration.observe(osp_vm_build_duration)
                        # self.osp_vm_build_duration.labels(hostname, osp_python_module, service_exporter).set(osp_vm_build_duration)
                    except Exception as e:
                        print ("Error osp_vm_build_duration is:  ", e)
                else:
                    try:
                        osp_count_event = data_load["osp_count_event"]
                        print ("osp_count_event is ", osp_count_event)
                        self.osp_count_event.labels(hostname, osp_python_module, osp_code_status, service_exporter).set(osp_count_event)
                    except Exception as e:
                        print ("Error osp_count_event is:  ", e)
        except Exception as e:
            print ("Error: JSONFILE can not to read ", e)
                
def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "10"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port, addr='172.17.0.1')
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()