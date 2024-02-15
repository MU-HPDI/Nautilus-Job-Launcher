from argparse import ArgumentParser
from .launcher import NautilusJobLauncher

parser = ArgumentParser(prog="python -m nautiluslauncher")
parser.add_argument("-c", "--cfg", required=True, help="Path to YAML config file")
parser.add_argument(
    "-b", "--base", required=False, help="Path to a base YAML config file", default=None
)
parser.add_argument(
    "-d",
    "--dryrun",
    required=False,
    default=False,
    action="store_true",
    help="Show the jobs that would be run",
)
parser.add_argument(
    "-i",
    "--ignore",
    action="store_true",
    required=False,
    default=False,
    help="When true, don't print stack trace for failed job launch",
)
parser.add_argument(
    "-j",
    "--jobs",
    required=False,
    default=None,
    nargs="*",
    help="Names of jobs in cfg to run. Defaults to all",
)
args = parser.parse_args()

NautilusJobLauncher.from_config(args.cfg, base_cfg_path=args.base).run(
    dryrun=args.dryrun, verbose_errors=not args.ignore, jobs=args.jobs
)
