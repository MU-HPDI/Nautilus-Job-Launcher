# Nautilus Job Launcher

This Nautilus Job Launcher is a Python library that enables automation of launching jobs on the NRP Nautlius HyperCluster. 

## Installation
To install the Nautilus Job Launcher, clone the repository and use `pip` to install it:
```
pip3 install nautilus-job-launcher
```

## Usage
**Note:** You must have your Kubernetes config file in `~/.kube/config` to use this library!

The Nautilus Launcher can be used as an application at the command line that will kick off jobs from a YAML config file, or it can be utilized as a library integrated into other Python applications. 

Details of these use cases are described below.

### Command Line Usage
The job launcher is invoked as a library and uses a configuration file (YAML):
```bash
python3 -m nautiluslauncher -c cfg.yaml
```

You can choose to perform a dryrun by passing a `--dryrun` flag:
```bash
python3 -m nautiluslauncher -c cfg.py --dryrun
```

### Library Usage
If you would like to integrate launching jobs with your application/library, you can choose to import them into your scripts instead:
```python
from nautiluslauncher import Job, NautilusAutomationClient

client = NautilusAutomationClient("mynamespace")
images = ["python:3.6", "python:3.7", "python:3.8"]
for i, img in enumerate(images):
    j = Job(job_name=f"test_python_{i}", image=i, command=["python", "-c", "print('hello world')"])
    client.create_job(j)
```

If you'd rather utilize a dictionary to configure your jobs and integrate that into your application:
```python
from nautiluslauncher import NautilusJobLauncher

my_jobs = {
    "namespace": "mynamespace",
    "jobs": [
        {"image": "python:3.6", command: ["python", "-c", "print('hello world')"], "job_name": "myjob1"}
        {"image": "python:3.7", command: ["python", "-c", "print('hello world')"], "job_name": "myjob2"}
        {"image": "python:3.8", command: ["python", "-c", "print('hello world')"], "job_name": "myjob3"}
    ]
}

launcher = NautilusJobLauncher(my_jobs)
launcher.run()
```

Or from a YAML file:
```python
from nautiluslauncher import NautilusJobLauncher

my_file = "myCfg.yaml"

launcher = NautilusJobLauncher.from_config(my_file)
launcher.run()
```

## Configuration
Configuration is done via a YAML file. There are sample YAML configs in the `configs` directory of this repository.

### Required Keys
There are two required keys and one optional key. The two required keys are:
- namespace
- jobs

The `namespace` is the namespace on the Nautilus cluster you'd like to use. The `jobs` key is a list of dictionaries that define all of the parameters for each job. However this process is made easier using the third optional key: `defaults`.

### Describing a Job
| Key | Description | Default | Type |
|---|---|---|--|
| job_name | The name of the job | _required_ | str |
| image | The container image to use | _required_ | str | 
| command | The command to run when the job starts | _required_ | str/list[str] |
| workingDir | Working directory when the job starts | None | str |
| env | The environment variables | None | dict[str, str] |
| volumes | The volumes to mount | None | dict[str, str] |
| ports | The container ports to expose | None | list[int] |
| gpu_types | The types of GPUs required | None | list[str] |
| min_cpu | Minimum # of CPU Cores | 2 | int |
| max_cpu | Max # of CPU cores | 4 | int |
| min_ram | Min GB of RAM | 4 | int |
| max_ram | Max GB of RAM | 8 | int |
| gpu | # of GPUs | 0 | int |
| shm | When true, add shared memory mount | false | bool |

### Using Defaults

The `defaults` key is a starting place for all jobs in your config. All jobs will use the `defaults` as the beginning configuration and then whatever is placed in each job will be added to **or override** what is present in the `defaults` key. Note that when a key is present in both `defaults` and the job, the job will take precedence. 

Here is a simple example:
```
defaults:
    container: python:3.8
    workingDir: /mydir

jobs:
- 
    container: python:3.7
-
    workingDir: /mydir2
-
    container: python:3.7
    workingDir: /mydir2
```