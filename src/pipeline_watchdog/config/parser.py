import yaml

from src.pipeline_watchdog.config.config import *
from src.pipeline_watchdog.utils import convert_to_seconds


class ConfigParser:

    def __init__(self, config_path: str):
        self._config_path = config_path

    @staticmethod
    def __parse_queue_config(queue_config: dict):
        return QueueConfig(
            action=Action(queue_config['action']),
            length=queue_config['length'],
            restart_cooldown=convert_to_seconds(queue_config['restart_cooldown']),
            container_labels=[list(labels.values()) for labels in queue_config['restart']]
        )

    @staticmethod
    def __parse_flow_config(flow_config: dict):
        return FlowConfig(
            action=Action(flow_config['action']),
            idle=convert_to_seconds(flow_config['idle']),
            restart_cooldown=convert_to_seconds(flow_config['restart_cooldown']),
            container_labels=[list(labels.values()) for labels in flow_config['restart']]
        )

    def __parse_watch_config(self, watch_config: dict):
        return WatchConfig(
            buffer=watch_config['buffer'],
            queue=self.__parse_queue_config(watch_config['queue']),
            egress=self.__parse_flow_config(watch_config['egress']),
            ingress=self.__parse_flow_config(watch_config['ingress'])
        )

    def parse(self) -> Config:
        with open(self._config_path, 'r') as file:
            parsed_yaml = yaml.load(file, Loader=yaml.Loader)
            parsed_yaml['watch'] = [self.__parse_watch_config(w) for w in parsed_yaml['watch']]
            config = Config(**parsed_yaml)

        return config

