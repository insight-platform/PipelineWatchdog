import pytest

from src.pipeline_watchdog.config import WatchConfig
from src.pipeline_watchdog.config.parser import ConfigParser


def test_parse(config_file_path, watch_config):
    config = ConfigParser(config_file_path).parse()

    assert len(config.watch_configs) == 2
    assert config.watch_configs[0] == watch_config

    # check optional fields
    assert config.watch_configs[1] == WatchConfig(
        buffer='buffer2:8002', queue=None, egress=None, ingress=None
    )


def test_parse_empty(empty_config_file_path):
    with pytest.raises(
        ValueError,
        match='No watch configs found in the config file. Please specify at least one.',
    ):
        ConfigParser(empty_config_file_path).parse()


def test_parse_invalid(invalid_config_file_path):
    with pytest.raises(
        ValueError,
        match='Field ".*" must be specified in the watch config.',
    ):
        ConfigParser(invalid_config_file_path).parse()
