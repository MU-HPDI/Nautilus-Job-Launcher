from kubernetes.client import (
    V1ResourceRequirements,
    V1EnvVar,
    V1Volume,
    V1VolumeMount,
    V1PersistentVolumeClaimVolumeSource,
    V1PodTemplateSpec,
    V1ObjectMeta,
    V1PodSpec,
    V1JobSpec,
    V1Job,
    V1EmptyDirVolumeSource,
    V1Container,
    V1ContainerPort,
    V1Affinity,
    V1NodeAffinity,
    V1NodeSelector,
    V1NodeSelectorTerm,
    V1NodeSelectorRequirement,
)
from .utils import LOGGER

from typing import Union, List, Dict, Optional

MINCPU = 2
MAXCPU = 4

MINRAM = 4
MAXRAM = 8

MINGPU = 0


class Job:
    def __init__(
        self,
        job_name: str,
        image: str,
        command: Union[str, List[str]],
        workingDir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
        ports: Optional[List[int]] = None,
        gpu_types: Optional[List[str]] = None,
        region: Optional[str] = None,
        min_cpu: int = MINCPU,
        max_cpu: int = MAXCPU,
        min_ram: int = MINRAM,
        max_ram: int = MAXRAM,
        gpu: int = MINGPU,
        shm: bool = False,
    ):
        #########
        # Param Check
        #########
        # fmt: off
        assert job_name is not None and isinstance(job_name, str), "Job name must be a string"
        assert image is not None and isinstance(image, str), "Image must be a string"
        assert command is not None and isinstance(command, (str, list)), "Command must be str or list"
        assert workingDir is None or isinstance(workingDir, str), "Working dir must be None or string"
        assert ports is None or isinstance(ports, list), "Ports must be None or list"
        assert gpu_types is None or isinstance(gpu_types, list), "Gpu Types must be None or list"
        assert region is None or isinstance(region, str), "Region must be None or string"
        assert env is None or isinstance(env, dict), "Env must be dict or None"
        assert volumes is None or isinstance(volumes, dict), "Volumes must be dict or None"
        assert all(isinstance(resource, int) for resource in \
                   [min_cpu, max_cpu, min_ram, max_ram, gpu]), "All resources must be int"
        assert isinstance(shm, bool), "Shm must be boolean"
        # fmt: on

        #########
        # Save to Class
        #########
        self.job_name = job_name
        self.image = image
        self.command = command
        self.workingDir = workingDir

        ########
        # Ports
        ########
        self.ports = None
        if ports is not None and len(ports) > 0:
            LOGGER.debug("Found ports in cfg: {ports}")
            self.ports = [V1ContainerPort(container_port=p) for p in ports]

        #########
        # Resources
        #########
        self.resources = V1ResourceRequirements(
            requests={"cpu": min_cpu, "memory": f"{min_ram}Gi", "nvidia.com/gpu": gpu},
            limits={
                "cpu": max(min_cpu, max_cpu),
                "memory": f"{max(min_ram, max_ram)}Gi",
                "nvidia.com/gpu": gpu,
            },
        )

        ####
        # Affinity
        ####
        self.affinity = None
        affinity_terms = []

        ####
        # GPU Affinity
        ####
        if gpu > 0 and gpu_types is not None and len(gpu_types) > 0:
            LOGGER.debug(
                f"Found gpu_types and GPU > 0. Setting node affinity: {gpu_types}"
            )
            affinity_terms.append(
                V1NodeSelectorRequirement(
                    key="nvidia.com/gpu.product",
                    operator="In",
                    values=gpu_types,
                )
            )
        ####
        # Region Affinity
        ####
        if region is not None:
            affinity_terms.append(
                V1NodeSelectorRequirement(
                    key="topology.kubernetes.io/region",
                    operator="In",
                    values=[region],
                )
            )

        ####
        # Set affinity if necessary
        ####
        if len(affinity_terms) > 0:
            self.affinity = V1Affinity(
                node_affinity=V1NodeAffinity(
                    required_during_scheduling_ignored_during_execution=V1NodeSelector(
                        node_selector_terms=[
                            V1NodeSelectorTerm(match_expressions=affinity_terms)
                        ]
                    )
                )
            )

        #########
        # Volumes
        #########
        self.volumes = None
        self.volume_mounts = None
        if volumes is not None:
            LOGGER.debug(
                f"Found volumes for this job. Mounting PVCs: {list(volumes.keys())}"
            )
            self.volume_mounts = [
                V1VolumeMount(mount_path=path, name=name)
                for name, path in volumes.items()
            ]
            self.volumes = [
                V1Volume(
                    name=v,
                    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
                        claim_name=v
                    ),
                )
                for v in volumes.keys()
            ]

        #########
        # Shared Memory
        #########
        if shm is True:
            LOGGER.debug("Found shm = True. Adding dshm volume for PyTorch")
            if self.volumes is None:
                self.volumes = []
            if self.volume_mounts is None:
                self.volume_mounts = []

            shm_mount = V1VolumeMount(mount_path="/dev/shm", name="dshm")
            shm_volume = V1Volume(
                name="dshm", empty_dir=V1EmptyDirVolumeSource(medium="Memory")
            )

            self.volume_mounts.append(shm_mount)
            self.volumes.append(shm_volume)

        ##########
        # Environment
        ##########
        self.env = None
        if env is not None and len(env) > 0:
            LOGGER.debug(
                f"Found environment variables. Adding to container: {list(env.keys())}"
            )
            self.env = [
                V1EnvVar(name=name, value=str(value)) for name, value in env.items()
            ]

    def create_job_object(self):
        # create container object
        container = V1Container(
            name=f"{self.job_name}-container",
            image=self.image,
            command=self.command,
            working_dir=self.workingDir,
            env=self.env,
            resources=self.resources,
            volume_mounts=self.volume_mounts,
            ports=self.ports,
            image_pull_policy="IfNotPresent",
        )

        # Create and configure a spec section
        template = V1PodTemplateSpec(
            metadata=V1ObjectMeta(labels={"app": self.job_name}),
            spec=V1PodSpec(
                restart_policy="Never",
                containers=[container],
                volumes=self.volumes,
                affinity=self.affinity,
            ),
        )
        # Create the specification of deployment
        spec = V1JobSpec(
            template=template, backoff_limit=0, ttl_seconds_after_finished=604800
        )
        # Instantiate the job object
        job = V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=V1ObjectMeta(name=self.job_name),
            spec=spec,
        )

        return job

    def __call__(self):
        return self.create_job_object()
