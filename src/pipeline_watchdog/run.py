import asyncio
import logging
import os
import re
import signal
import time
from typing import Dict, List

import docker
import requests
from docker.errors import DockerException
from docker.models.containers import Container

from src.pipeline_watchdog.config import WatchConfig, QueueConfig, FlowConfig, Action
from src.pipeline_watchdog.config.parser import ConfigParser
from src.pipeline_watchdog.utils import init_logging

METRIC_PATTERN = re.compile(r'(\w+){[^}]*} ([0-9.e+-]+) \d+')
LOG_LEVEL = os.environ.get('LOGLEVEL', 'INFO')

init_logging(LOG_LEVEL)
logger = logging.getLogger('PipelineWatchdog')


class DockerClient:

    def __init__(self):
        self._client = docker.from_env()

    def get_containers(self, container_labels: List[List[str]]) -> List[Container]:
        containers = []
        for labels in container_labels:
            containers += self._client.containers.list(filters={"label": labels})

        return containers

    @staticmethod
    def restart_container(container: Container):
        try:
            container.restart()
        except DockerException:
            logger.error('Failed to restart container %s. Skipping', container.name)

    @staticmethod
    def stop_container(container: Container):
        try:
            container.stop()
        except DockerException:
            logger.error('Failed to stop container %s. Skipping', container.name)

    def __del__(self):
        self._client.close()


def get_metrics(buffer_url: str) -> requests.Response:
    try:
        response = requests.get(f'http://{buffer_url}/metrics')
        return response
    except requests.RequestException as e:
        raise RuntimeError(f'Failed to get metrics from {buffer_url}. {e}')


def parse_metrics(response: requests.Response) -> Dict[str, float]:
    metrics = {}

    try:
        for match in METRIC_PATTERN.finditer(response.text):
            metric, value = match.groups()
            metrics[metric] = float(value)
    except Exception as e:
        raise RuntimeError(f'Failed to parse metrics: {e}')

    return metrics


def process_action(docker_client: DockerClient, action: Action, container_labels: List[List[str]]):
    containers = docker_client.get_containers(container_labels)

    if action == Action.STOP:
        logger.debug('Stopping containers')
        for container in containers:
            docker_client.stop_container(container)
    elif action == Action.RESTART:
        logger.debug('Restarting containers')
        for container in containers:
            docker_client.restart_container(container)
    else:
        raise RuntimeError(f'Unknown action {action}')


async def watch_queue(docker_client: DockerClient, buffer: str, config: QueueConfig):
    while True:
        response = get_metrics(buffer)
        metrics = parse_metrics(response)

        buffer_size = metrics['buffer_size']

        if buffer_size > config.length:
            logger.debug('Buffer %s is full, processing action %s', buffer, config.action)
            process_action(docker_client, config.action, config.container_labels)

        await asyncio.sleep(config.restart_cooldown)


async def watch_egress(docker_client: DockerClient, buffer: str, config: FlowConfig):
    while True:
        response = get_metrics(buffer)
        metrics = parse_metrics(response)

        last_sent_message = metrics['last_sent_message']
        now = time.time()

        if now - last_sent_message > config.idle:
            logger.debug('Egress flow %s is idle, processing action %s', buffer, config.action)
            process_action(docker_client, config.action, config.container_labels)

        await asyncio.sleep(config.restart_cooldown)


async def watch_ingress(docker_client: DockerClient, buffer: str, config: FlowConfig):
    while True:
        response = get_metrics(buffer)
        metrics = parse_metrics(response)

        last_received_message = metrics['last_received_message']
        now = time.time()

        if now - last_received_message > config.idle:
            logger.debug('Ingress flow %s is idle, processing action %s', buffer, config.action)
            process_action(docker_client, config.action, config.container_labels)

        await asyncio.sleep(config.restart_cooldown)


async def watch_buffer(docker_client: DockerClient, config: WatchConfig):
    logger.info('Watching buffer metrics %s', config.buffer)
    await asyncio.gather(
        watch_queue(docker_client, config.buffer, config.queue),
        watch_egress(docker_client, config.buffer, config.egress),
        watch_ingress(docker_client, config.buffer, config.ingress)
    )


def main():
    # To gracefully shutdown the adapter on SIGTERM (raise KeyboardInterrupt)
    signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))

    config_file_path = os.environ.get('CONFIG_FILE_PATH')
    if not config_file_path:
        logger.error('Configuration file path is not provided. Provide the CONFIG_FILE_PATH environment variable')
        exit(1)

    parser = ConfigParser(config_file_path)

    try:
        config = parser.parse()
    except Exception as e:
        logger.error('Failed to parse configuration. %s: %s', type(e).__name__, e)
        exit(1)

    docker_client = DockerClient()

    loop = asyncio.get_event_loop()
    futures = asyncio.gather(*[watch_buffer(docker_client, x) for x in config.watch_configs])
    try:
        loop.run_until_complete(futures)
    except KeyboardInterrupt:
        logger.error('Shutting down the pipeline watchdog')
    finally:
        loop.close()


if __name__ == '__main__':
    main()
