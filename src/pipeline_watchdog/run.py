#!/usr/bin/env python3

import asyncio
import logging
import os
import re
import signal
import time
from typing import Dict, List

import aiodocker
import aiohttp
from aiodocker import DockerError
from aiodocker.containers import DockerContainer

from src.pipeline_watchdog.config import Action, FlowConfig, QueueConfig, WatchConfig
from src.pipeline_watchdog.config.parser import ConfigParser
from src.pipeline_watchdog.config.validator import validate
from src.pipeline_watchdog.utils import init_logging

METRIC_PATTERN = re.compile(r'(\w+){[^}]*} ([0-9.e+-]+) \d+')
LOG_LEVEL = os.environ.get('LOGLEVEL', 'INFO')

init_logging(LOG_LEVEL)
logger = logging.getLogger('PipelineWatchdog')


class DockerClient:

    def __init__(self):
        self._client = aiodocker.Docker()

    async def get_containers(
        self, container_labels: List[List[str]]
    ) -> List[DockerContainer]:
        containers = []
        for labels in container_labels:
            try:
                containers += await self._client.containers.list(
                    all=True, filters={'label': labels}
                )
            except DockerError:
                raise RuntimeError(f'Failed to list containers with labels {labels}')

        return containers

    @staticmethod
    async def restart_container(container: DockerContainer):
        try:
            await container.restart()
            logger.debug('Container %s restarted', container.id)
        except DockerError:
            logger.error('Failed to restart container %s. Skipping', container.id)

    @staticmethod
    async def stop_container(container: DockerContainer):
        try:
            await container.stop()
            logger.debug('Container %s stopped', container.id)
        except DockerError:
            logger.error('Failed to stop container %s. Skipping', container.id)

    async def close(self):
        await self._client.close()


async def get_metrics(buffer_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{buffer_url}/metrics') as response:
            content = await response.text()
            return content


async def parse_metrics(content: str) -> Dict[str, float]:
    metrics = {}

    try:
        for match in METRIC_PATTERN.finditer(content):
            metric, value = match.groups()
            metrics[metric] = float(value)
    except Exception as e:
        raise RuntimeError(f'Failed to parse metrics: {e}')

    return metrics


async def process_action(
    docker_client: DockerClient, action: Action, container_labels: List[List[str]]
):
    containers = await docker_client.get_containers(container_labels)

    if not containers:
        logger.debug('No containers found with labels %s', container_labels)
        return

    if action == Action.STOP:
        logger.debug('Stopping containers')
        for container in containers:
            await docker_client.stop_container(container)
    elif action == Action.RESTART:
        logger.debug('Restarting containers')
        for container in containers:
            await docker_client.restart_container(container)
    else:
        raise RuntimeError(f'Unknown action {action}')


async def watch_queue(docker_client: DockerClient, buffer: str, config: QueueConfig):
    while True:
        content = await get_metrics(buffer)
        metrics = await parse_metrics(content)

        buffer_size = metrics['buffer_size']

        if buffer_size > config.length:
            logger.debug(
                'Buffer %s is full, processing action %s', buffer, config.action
            )
            await process_action(docker_client, config.action, config.container_labels)

        await asyncio.sleep(config.restart_cooldown)


async def watch_egress(docker_client: DockerClient, buffer: str, config: FlowConfig):
    while True:
        content = await get_metrics(buffer)
        metrics = await parse_metrics(content)

        last_sent_message = metrics['last_sent_message']
        now = time.time()

        if now - last_sent_message > config.idle:
            logger.debug(
                'Egress flow %s is idle, processing action %s', buffer, config.action
            )
            await process_action(docker_client, config.action, config.container_labels)

        await asyncio.sleep(config.restart_cooldown)


async def watch_ingress(docker_client: DockerClient, buffer: str, config: FlowConfig):
    while True:
        content = await get_metrics(buffer)
        metrics = await parse_metrics(content)

        last_received_message = metrics['last_received_message']
        now = time.time()

        if now - last_received_message > config.idle:
            logger.debug(
                'Ingress flow %s is idle, processing action %s', buffer, config.action
            )
            await process_action(docker_client, config.action, config.container_labels)

        await asyncio.sleep(config.restart_cooldown)


async def watch_buffer(docker_client: DockerClient, config: WatchConfig):
    logger.info('Watching buffer metrics %s', config.buffer)
    await asyncio.gather(
        watch_queue(docker_client, config.buffer, config.queue),
        watch_egress(docker_client, config.buffer, config.egress),
        watch_ingress(docker_client, config.buffer, config.ingress),
    )


def main():
    # To gracefully shutdown the adapter on SIGTERM (raise KeyboardInterrupt)
    signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))

    config_file_path = os.environ.get('CONFIG_FILE_PATH')
    if not config_file_path:
        logger.error(
            'Configuration file path is not provided. Provide the CONFIG_FILE_PATH environment variable'
        )
        exit(1)

    parser = ConfigParser(config_file_path)

    try:
        config = parser.parse()
        validate(config)
    except Exception as e:
        logger.error('Invalid configuration. %s: %s', type(e).__name__, e)
        exit(1)

    docker_client = DockerClient()

    loop = asyncio.get_event_loop()
    futures = asyncio.gather(
        *[watch_buffer(docker_client, x) for x in config.watch_configs]
    )
    try:
        loop.run_until_complete(futures)
    except KeyboardInterrupt:
        logger.error('Shutting down the pipeline watchdog')
    finally:
        loop.close()
        asyncio.run(docker_client.close())


if __name__ == '__main__':
    main()
