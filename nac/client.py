from kubernetes import config, client
from pprint import pprint

from .job import Job


class NautilusAutomationClient:
    def __init__(self, namespace, defaults=None):

        config.load_kube_config()

        self.nautilus = client.BatchV1Api()
        self.namespace = namespace
        self.defaults = defaults

    def create_job(self, job: Job):
        return self.nautilus.create_namespaced_job(body=job(), namespace=self.namespace)

    def list_pods(self):
        v1 = client.CoreV1Api()
        ret = v1.list_namespaced_pod(self.namespace)
        pprint(ret)
