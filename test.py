from kubernetes import client, config

JOB_NAME = "pi"
NAMESPACE = "gpn-mizzou-jhurt"

RESOURCES = client.V1ResourceRequirements(
    requests={
        "cpu": "1",
        "memory": "8Gi",
    },
    limits={
        "cpu": "4",
        "memory": "24Gi",
    },
)


def create_job_object():
    # Configureate Pod template container
    container = client.V1Container(
        name="pi",
        image="perl",
        command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"],
        resources=RESOURCES,
    )
    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "pi"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
    )
    # Create the specification of deployment
    spec = client.V1JobSpec(template=template, backoff_limit=4)
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=JOB_NAME),
        spec=spec,
    )

    return job


def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(body=job, namespace=NAMESPACE)
    print("Job created. status='%s'" % str(api_response.status))


if __name__ == "__main__":
    config.load_kube_config()

    batch_v1 = client.BatchV1Api()

    job = create_job_object()

    create_job(batch_v1, job)
