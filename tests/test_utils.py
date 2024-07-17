import sys
from unittest import mock

import pytest

from src.pipeline_watchdog.utils import convert_to_seconds, init_logging


@mock.patch('logging.basicConfig')
def test_init_logging(basic_config_mock):
    log_level = 'DEBUG'

    init_logging(log_level)

    basic_config_mock.assert_called_once_with(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=log_level,
    )


@pytest.mark.parametrize(
    'string, expected',
    [
        ('0s', 0),
        ('1s', 1),
        ('1m', 60),
        ('1h', 3600),
        ('1d', 86400),
        ('1w', 604800),
    ],
)
def test_convert_to_seconds(string, expected):
    assert convert_to_seconds(string) == expected


@pytest.mark.parametrize(
    'string, expected_error',
    [
        ('1x', KeyError),
        ('-1s', ValueError),
        ('xs', ValueError),
        ('xx', ValueError),
    ],
)
def test_convert_to_seconds_invalid_input(string, expected_error):
    with pytest.raises(expected_error):
        convert_to_seconds(string)
