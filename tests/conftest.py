import copy
import os

import pytest
import yaml

from src.pipeline_watchdog.config import Action, FlowConfig, QueueConfig, WatchConfig
from src.pipeline_watchdog.config.config import Config


@pytest.fixture(scope='session')
def watch_config() -> WatchConfig:
    return WatchConfig(
        buffer='buffer1:8000',
        queue=QueueConfig(
            action=Action.RESTART,
            length=18,
            restart_cooldown=60,
            container_labels=[['label1', 'label2=2'], ['some-label']],
        ),
        egress=FlowConfig(
            action=Action.STOP,
            idle=100,
            restart_cooldown=60,
            container_labels=[['egress-label=egress-value'], ['some-label']],
        ),
        ingress=FlowConfig(
            action=Action.RESTART,
            idle=60,
            restart_cooldown=30,
            container_labels=[['some-label']],
        ),
    )


@pytest.fixture(scope='session')
def config(watch_config) -> Config:
    return Config(watch_configs=[watch_config])


@pytest.fixture(scope='session')
def config_with_queue_only(watch_config) -> Config:
    new_watch_config = copy.deepcopy(watch_config)
    new_watch_config.ingress = None
    new_watch_config.egress = None

    return Config(watch_configs=[new_watch_config])


@pytest.fixture(scope='session')
def config_with_ingress_only(watch_config) -> Config:
    new_watch_config = copy.deepcopy(watch_config)
    new_watch_config.queue = None
    new_watch_config.egress = None

    return Config(watch_configs=[new_watch_config])


@pytest.fixture(scope='session')
def config_with_egress_only(watch_config) -> Config:
    new_watch_config = copy.deepcopy(watch_config)
    new_watch_config.queue = None
    new_watch_config.ingress = None

    return Config(watch_configs=[new_watch_config])


@pytest.fixture(scope='session')
def config_with_invalid_watch_config() -> Config:
    return Config(watch_configs=[WatchConfig('buffer:8000', None, None, None)])


@pytest.fixture(scope='session')
def config_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_config.yml')


@pytest.fixture(
    params=(
        '',
        'watch',
        'watch:',
        'watch: []',
        'some-key: some-value',
    )
)
def empty_config_file_path(request, tmpdir):
    config_file = tmpdir.join('empty_config.txt')
    config_file.write(request.param)

    return str(config_file)


@pytest.fixture(
    params=(
        {'watch': [{'some-key': 'some-value'}]},
        {'watch': [{'buffer': 'buffer1:8000', 'queue': {'action': 'restart'}}]},
        {'watch': [{'buffer': 'buffer1:8000', 'egress': {'action': 'restart'}}]},
        {'watch': [{'buffer': 'buffer1:8000', 'ingress': {'action': 'restart'}}]},
    )
)
def invalid_config_file_path(request, tmpdir):
    config_file = tmpdir.join('empty_config.txt')

    yaml_str = yaml.dump(request.param)
    config_file.write(yaml_str)

    return str(config_file)
