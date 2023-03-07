from kubernetes import config, client
from pprint import pprint

from .job import Job


class NautilusAutomationClient:
    def __init__(self, namespace):
        config.load_kube_config()

        self.batchV1 = client.BatchV1Api()
        self.v1 = client.CoreV1Api()
        self.namespace = namespace

    def create_job(self, job: Job):
        return self.batchV1.create_namespaced_job(body=job(), namespace=self.namespace)

    def list_pods(self):
        ret = self.v1.list_namespaced_pod(self.namespace)
        return ret
