# This file contains the configuration classes for the pipeline watchdog
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


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

    cooldown: int
    """Interval in seconds to wait after applying the action."""

    polling_interval: int
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

    cooldown: int
    """Interval in seconds to wait after applying the action."""

    polling_interval: Optional[int]
    """Interval in seconds between buffer traffic checks."""

    container_labels: List[List[str]]
    """List of labels to filter the containers to which the action is applied."""


@dataclass
class WatchConfig:
    """Configuration for a single buffer."""

    buffer: str
    """Buffer url to retrieve metrics."""

    queue: Optional[QueueConfig]
    """Queue watch configuration."""

    egress: Optional[FlowConfig]
    """Egress traffic watch configuration."""

    ingress: Optional[FlowConfig]
    """Ingress traffic watch configuration."""


@dataclass
class Config:
    """Pipeline watchdog configuration."""

    watch_configs: List[WatchConfig]
    """List of buffer watch configurations."""
