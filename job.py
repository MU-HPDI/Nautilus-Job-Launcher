from kubernetes import client
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
        volumes: Union[None, Dict[str, str]] = None,
        min_cpu: int = MINCPU,
        max_cpu: int = MAXCPU,
        min_ram: int = MINRAM,
        max_ram: int = MAXRAM,
        gpu: int = MINGPU,
        shm: bool = False,
    ):
        # fmt: off
        assert job_name is not None and isinstance(job_name, str), "Job name must be a string"
        assert image is not None and isinstance(image, str), "Image must be a string"
        assert command is not None and isinstance(command, (str, list)), "Command must be str or list"
        assert volumes is None or isinstance(volumes, dict), "Volumes must be dict or None"
        assert all(isinstance(resource, int) for resource in \
                   [min_cpu, max_cpu, min_ram, max_ram, gpu]), "All resources must be int"
        assert isinstance(shm, bool), "Shm must be boolean"
        # fmt: on

        self.job_name = job_name
        self.image = image
        self.command = command

        self.resources = client.V1ResourceRequirements(
            requests={"cpu": min_cpu, "memory": f"{min_ram}Gi", "nvidia.com/gpu": gpu},
            limits={
                "cpu": max(min_cpu, max_cpu),
                "memory": f"{max(min_ram, max_ram)}Gi",
                "nvidia.com/gpu": gpu,
            },
        )

        self.volumes = None
        self.volume_mounts = None
        if volumes is not None:
            self.volume_mounts = [
                client.V1VolumeMount(mount_path=path, name=name)
                for name, path in volumes.items()
            ]
            self.volumes = [
                client.V1Volume(
                    name=v,
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=v
                    ),
                )
                for v in volumes.keys()
            ]

        if shm is True:
            if self.volumes is None:
                self.volumes = []
            if self.volume_mounts is None:
                self.volume_mounts = []

            shm_mount = client.V1VolumeMount(mount_path="/dev/shm", name="dshm")
            shm_volume = client.V1Volume(
                name="dshm", empty_dir=client.V1EmptyDirVolumeSource(medium="Memory")
            )

            self.volume_mounts.append(shm_mount)
            self.volumes.append(shm_volume)

    def create_job_object(self):
        # create container object
        container = client.V1Container(
            name=f"{self.job_name}-container",
            image=self.image,
            command=self.command,
            resources=self.resources,
            volume_mounts=self.volume_mounts,
        )

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": self.job_name}),
            spec=client.V1PodSpec(
                restart_policy="Never", containers=[container], volumes=self.volumes
            ),
        )
        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template, backoff_limit=0, ttl_seconds_after_finished=60
        )
        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=self.job_name),
            spec=spec,
        )

        return job

    def __call__(self):
        return self.create_job_object()
