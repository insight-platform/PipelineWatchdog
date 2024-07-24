import re
from typing import Dict

import aiohttp

METRIC_PATTERN = re.compile(r'(\w+){[^}]*} ([0-9.e+-]+) \d+')


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
    except TypeError as e:
        raise RuntimeError(f'Failed to parse metrics: {e}')

    return metrics
