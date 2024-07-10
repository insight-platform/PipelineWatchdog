# This file contains the configuration classes for the pipeline watchdog

from enum import Enum
from typing import List


class Action(Enum):
    STOP = 'stop'
    RESTART = 'restart'


class QueueConfig:
    """Configuration to watch a buffer queue.

    :param action: Action to take when buffer queue is full.
    :param length: Maximum buffer queue length.
    :param restart_cooldown: Interval in seconds between buffer queue length checks.
    :param container_labels: List of labels to filter the containers to which the action is applied.
    """

    def __init__(self, action: Action, length: int, restart_cooldown: int, container_labels: List[List[str]]):
        self.action = action
        self.length = length
        self.restart_cooldown = restart_cooldown
        self.container_labels = container_labels


class FlowConfig:
    """Configuration to watch a buffer incoming or outgoing traffic.

    :param action: Action to take when buffer traffic is idle.
    :param idle: Maximum time in seconds buffer traffic can be idle.
    :param restart_cooldown: Interval in seconds between checks that buffer traffic is idle.
    :param container_labels: List of labels to filter the containers to which the action is applied.
    """

    def __init__(self, action: Action, idle: int, restart_cooldown: int, container_labels: List[List[str]]):
        self.action = action
        self.idle = idle
        self.restart_cooldown = restart_cooldown
        self.container_labels = container_labels


class WatchConfig:
    """Configuration for a single buffer.

    :param buffer: Buffer url to retrieve metrics.
    :param queue: Queue watch configuration.
    :param egress: Egress traffic watch configuration.
    :param ingress: Ingress traffic watch configuration.
    """

    def __init__(self, buffer: str, queue: QueueConfig, egress: FlowConfig, ingress: FlowConfig):
        self.buffer = buffer
        self.queue = queue
        self.egress = egress
        self.ingress = ingress


class Config:
    """Pipeline watchdog configuration.

    :param watch: List of buffer watch configurations.
    """

    def __init__(self, watch: List[WatchConfig]):
        self.watch_configs = watch
