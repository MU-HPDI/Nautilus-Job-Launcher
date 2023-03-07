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
)
from typing import Union, List, Dict

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
        workingDir: Union[None, str] = None,
        env: Union[None, Dict[str, str]] = None,
        volumes: Union[None, Dict[str, str]] = None,
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

        #########
        # Volumes
        #########
        self.volumes = None
        self.volume_mounts = None
        if volumes is not None:
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
            self.env = [V1EnvVar(name=name, value=value) for name, value in env.items()]

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
        )

        # Create and configure a spec section
        template = V1PodTemplateSpec(
            metadata=V1ObjectMeta(labels={"app": self.job_name}),
            spec=V1PodSpec(
                restart_policy="Never", containers=[container], volumes=self.volumes
            ),
        )
        # Create the specification of deployment
        spec = V1JobSpec(
            template=template, backoff_limit=0, ttl_seconds_after_finished=60
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
