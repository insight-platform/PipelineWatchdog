import os

import pytest
from omegaconf import ListConfig

from src.pipeline_watchdog.config import WatchConfig
from src.pipeline_watchdog.config.parser import ConfigParser


def test_parse(config_file_path, watch_config):
    os.environ['POLLING_INTERVAL'] = '20s'

    config = ConfigParser(config_file_path).parse()

    assert len(config.watch_configs) == 2
    assert config.watch_configs[0] == watch_config

    # check that OmegaConf types are properly converted
    assert not any(
        isinstance(labels, ListConfig)
        for container_labels in [
            config.watch_configs[0].queue.container_labels,
            config.watch_configs[0].egress.container_labels,
            config.watch_configs[0].ingress.container_labels,
        ]
        for labels in container_labels
    )
    assert all(
        isinstance(label, str)
        for container_labels in [
            config.watch_configs[0].queue.container_labels,
            config.watch_configs[0].egress.container_labels,
            config.watch_configs[0].ingress.container_labels,
        ]
        for labels in container_labels
        for label in labels
    )

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


def test_parse_empty_labels(invalid_config_with_empty_labels):
    with pytest.raises(
        ValueError,
        match='Container labels cannot be empty.',
    ):
        ConfigParser(invalid_config_with_empty_labels).parse()
