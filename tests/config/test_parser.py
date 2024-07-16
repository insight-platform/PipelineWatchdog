from src.pipeline_watchdog.config import QueueConfig, WatchConfig, Action, FlowConfig
from src.pipeline_watchdog.config.parser import ConfigParser


def test_parse():
    config = ConfigParser("../test_config.yml").parse()

    assert len(config.watch_configs) == 2
    assert config.watch_configs[0] == WatchConfig(
        buffer='buffer1:8000',
        queue=QueueConfig(
            action=Action.RESTART,
            length=18,
            restart_cooldown=60,
            container_labels=[['label1', 'label2=2'], ['some-label']]
        ),
        egress=FlowConfig(
            action=Action.STOP,
            idle=100,
            restart_cooldown=60,
            container_labels=[['egress-label=egress-value'], ['some-label']]
        ),
        ingress=FlowConfig(
            action=Action.RESTART,
            idle=60,
            restart_cooldown=30,
            container_labels=[['some-label']]
        )
    )
    assert config.watch_configs[1] == WatchConfig(
        buffer='buffer2:8002',
        queue=QueueConfig(
            action=Action.STOP,
            length=999,
            restart_cooldown=50,
            container_labels=[['some-label']]
        ),
        egress=FlowConfig(
            action=Action.RESTART,
            idle=100,
            restart_cooldown=90,
            container_labels=[['egress-label=egress-value']]
        ),
        ingress=FlowConfig(
            action=Action.STOP,
            idle=70,
            restart_cooldown=60,
            container_labels=[['some-label']]
        )
    )
