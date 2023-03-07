from argparse import ArgumentParser
from .launcher import NautilusJobLauncher

parser = ArgumentParser(prog="python -m nautiluslauncher")
parser.add_argument("-c", "--cfg", required=True, help="Path to YAML config file")
args = parser.parse_args()

NautilusJobLauncher.from_config(args.cfg).run()
