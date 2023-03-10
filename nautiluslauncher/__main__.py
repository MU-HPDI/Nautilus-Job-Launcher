from argparse import ArgumentParser
from .launcher import NautilusJobLauncher

parser = ArgumentParser(prog="python -m nautiluslauncher")
parser.add_argument("-c", "--cfg", required=True, help="Path to YAML config file")
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
args = parser.parse_args()

NautilusJobLauncher.from_config(args.cfg).run(
    dryrun=args.dryrun, verbose_errors=not args.ignore
)
