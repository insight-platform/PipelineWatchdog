import yaml

from src.pipeline_watchdog.config.config import *
from src.pipeline_watchdog.utils import convert_to_seconds


class ConfigParser:

    def __init__(self, config_path: str):
        self._config_path = config_path

    @staticmethod
    def __parse_labels(labels_list: list) -> list:
        labels = []
        for label_dict in labels_list:
            for label in label_dict.values():
                if isinstance(label, list):
                    labels.append(label)
                else:
                    labels.append([label])
        return labels

    @staticmethod
    def __parse_queue_config(queue_config: dict):
        if queue_config is None:
            return None

        return QueueConfig(
            action=Action(queue_config['action']),
            length=queue_config['length'],
            restart_cooldown=convert_to_seconds(queue_config['restart_cooldown']),
            container_labels=ConfigParser.__parse_labels(queue_config['container']),
        )

    @staticmethod
    def __parse_flow_config(flow_config: dict):
        if flow_config is None:
            return None

        return FlowConfig(
            action=Action(flow_config['action']),
            idle=convert_to_seconds(flow_config['idle']),
            restart_cooldown=convert_to_seconds(flow_config['restart_cooldown']),
            container_labels=ConfigParser.__parse_labels(flow_config['container']),
        )

    @staticmethod
    def __parse_watch_config(watch_config: dict):
        return WatchConfig(
            buffer=watch_config['buffer'],
            queue=ConfigParser.__parse_queue_config(watch_config.get('queue')),
            egress=ConfigParser.__parse_flow_config(watch_config.get('egress')),
            ingress=ConfigParser.__parse_flow_config(watch_config.get('ingress')),
        )

    def parse(self) -> Config:
        with open(self._config_path, 'r') as file:
            parsed_yaml = yaml.load(file, Loader=yaml.FullLoader)
            watch = parsed_yaml.get('watch')

            if not watch:
                raise ValueError(
                    'No watch configs found in the config file. Please specify at least one.'
                )

            config = Config([self.__parse_watch_config(w) for w in watch])

        return config
