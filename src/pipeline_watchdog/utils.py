import logging
import sys

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def init_logging(loglevel: str):
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=loglevel
    )


def convert_to_seconds(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]
