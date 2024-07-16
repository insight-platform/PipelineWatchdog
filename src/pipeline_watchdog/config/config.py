# This file contains the configuration classes for the pipeline watchdog
from dataclasses import dataclass
from enum import Enum
from typing import List


class Action(Enum):
    STOP = 'stop'
    RESTART = 'restart'


@dataclass
class QueueConfig:
    """Configuration to watch a buffer queue."""

    action: Action
    """Action to take when buffer queue is full."""

    length: int
    """Maximum buffer queue length."""

    restart_cooldown: int
    """Interval in seconds between buffer queue length checks."""

    container_labels: List[List[str]]
    """List of labels to filter the containers to which the action is applied."""


@dataclass
class FlowConfig:
    """Configuration to watch a buffer incoming or outgoing traffic."""

    action: Action
    """Action to take when buffer traffic is idle."""

    idle: int
    """Maximum time in seconds buffer traffic can be idle."""

    restart_cooldown: int
    """Interval in seconds between checks that buffer traffic is idle."""

    container_labels: List[List[str]]
    """List of labels to filter the containers to which the action is applied."""


@dataclass
class WatchConfig:
    """Configuration for a single buffer."""

    buffer: str
    """Buffer url to retrieve metrics."""

    queue: QueueConfig
    """Queue watch configuration."""

    egress: FlowConfig
    """Egress traffic watch configuration."""

    ingress: FlowConfig
    """Ingress traffic watch configuration."""


@dataclass
class Config:
    """Pipeline watchdog configuration."""

    watch_configs: List[WatchConfig]
    """List of buffer watch configurations."""
