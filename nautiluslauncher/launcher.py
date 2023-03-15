import warnings
import logging
from urllib3.connectionpool import InsecureRequestWarning
from .client import NautilusAutomationClient
from .job import Job
import yaml
from copy import deepcopy
import collections.abc
from pprint import pprint, pformat
from .utils import LOGGER


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

    def run(self, dryrun=False, jobs=None, verbose_errors=True):
        specs = []
        n_failed = 0
        logStatus = LOGGER.exception if verbose_errors else LOGGER.debug

        for jobSpec in self.jobs:
            ####
            # Get updated spec
            ####
            jobSpec = update(deepcopy(self.defaults), jobSpec)

            ####
            # Check name
            ####
            if jobs is not None and jobSpec["job_name"] not in jobs:
                LOGGER.debug(f"Skipping job {jobSpec['job_name']}; not found in jobs")
                continue

            ####
            # add to specs
            ####
            specs.append(jobSpec)
            LOGGER.debug(jobSpec)

            ####
            # Create job
            #####
            job = Job(**jobSpec)

            if not dryrun:
                try:
                    self.nac.create_job(job)
                    LOGGER.info(f"Successfully created job: {job.job_name}")
                except Exception as e:
                    n_failed += 1
                    logStatus(f"Failed to create job: {job.job_name}", exc_info=e)

        if not verbose_errors and not dryrun:
            LOGGER.info(f"Failed to create {n_failed} jobs")

        if dryrun:
            LOGGER.info("\n" + pformat(specs))
