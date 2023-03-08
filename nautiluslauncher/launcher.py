import warnings
from urllib3.connectionpool import InsecureRequestWarning
from .client import NautilusAutomationClient
from .job import Job
import yaml
from copy import deepcopy
import collections.abc
from pprint import pprint


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


REQUIRED_KEYS = {"namespace", "jobs"}


class NautilusJobLauncher:
    @classmethod
    def from_config(cls, cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.full_load(f)
        return cls(cfg)

    def __init__(self, cfg):
        assert isinstance(cfg, dict), "Config must be dictionary"
        assert all(k in REQUIRED_KEYS for k in REQUIRED_KEYS), "Missing required key"
        assert len(cfg["jobs"]) > 0, "Found 0 jobs"

        self.cfg = cfg
        self.defaults = cfg.get("defaults", dict())
        self.jobs = cfg["jobs"]

        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=InsecureRequestWarning)
            self.nac = NautilusAutomationClient(cfg["namespace"])

    def run(self, dryrun=False):
        specs = []
        for jobSpec in self.jobs:
            jobSpec = update(deepcopy(self.defaults), jobSpec)
            specs.append(jobSpec)
            job = Job(**jobSpec)
            if not dryrun:
                try:
                    self.nac.create_job(job)
                    print(f"Successfully created job: {job.job_name}")
                except Exception:
                    print(f"Failed to create job: {job.job_name}")

        if dryrun:
            pprint(specs)
