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
args = parser.parse_args()

NautilusJobLauncher.from_config(args.cfg).run(dryrun=args.dryrun)
