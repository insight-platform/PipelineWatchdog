# Watchdog
This service watches the health of pipeline by monitoring one or more buffers in parallel.
It will restart designated pipeline services if the buffer queue length exceeds a threshold value or the time since the last output or input message exceeds a specified time. 
Queue monitoring helps detect the slow processing of messages, and ingress and egress monitoring is helpful in detecting pipeline services that are not processing messages.

## Configuration

The watchdog service is configured using the following environment variables:
* `CONFIG_FILE_PATH` - The path to the configuration file. Required.
* `LOGLEVEL` - The log level for the service. Default is `INFO`.

Configuration file is YAML file with the following structure:
```yaml
watch:
    - buffer: <str>
      queue:
        action: <restart|stop>
        length: <int>
        restart_cooldown: <int>
        container:
          - labels: [<str>]
          # other labels
      egress:
        action: <restart|stop>
        idle: <int>
        restart_cooldown: <int>
        container:
          - labels: [<str>]
      ingress:
        action: <restart|stop>
        idle: <int>
        restart_cooldown: <int>
        container:
          - labels: [<str>]
          # other labels
    # other buffers
```

Where:
* `buffer` - url of the buffer to watch.
* `queue` - configuration for the buffer queue.
  * `action` - action to take when the queue length exceeds the length threshold. It can be `restart` or `stop`.
  * `length` - threshold length for the queue.
  * `restart_cooldown` - interval in seconds between buffer queue length checks.
  * `container` - list of labels to match for the action. Actions are performed on containers that match any of the label sets.
    * `labels` - one or more labels to match on the same container, i.e. the container must have all labels.
* `ingress` or `egress` - configuration for the input or output traffic.
  * `action` - action to take when the time since the last input or output message exceeds the idle threshold. It can be `restart` or `stop`.
  * `idle` - threshold time in seconds since the last input or output message.
  * `restart_cooldown` - interval in seconds between ingress or egress idle checks.
  * `container` - list of labels to match for the action. Actions are performed on containers that match any of the label sets.
    * `labels` - one or more labels to match on the same container, i.e. the container must have all labels.


## Sample

The sample demonstrates how to start the watchdog service with an example pipeline to watch the buffer and restart the SDK client based on configuration.

### Run

```bash
docker compose -f samples/pipeline_monitoring/docker-compose.yml up --build -d
```

### Stop

```bash
docker compose -f samples/pipeline_monitoring/docker-compose.yml down -v
```
