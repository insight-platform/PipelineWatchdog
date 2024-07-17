# Watchdog
This service watches the health of pipeline by monitoring one or more buffers in parallel.
It will stop or restart designated pipeline services if the buffer queue length exceeds a threshold value or the time since the last output or input message exceeds a specified time. 
Queue monitoring helps detect the slow processing of messages, and ingress and egress monitoring is helpful in detecting how pipeline services are processing messages. 
In other words, the service can detect if the pipeline is not processing messages at the expected rate or if the pipeline is not processing messages at all.

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
* `queue` - configuration for the buffer queue. Optional.
  * `action` - action to take when the queue length exceeds the length threshold. It can be `restart` or `stop`.
  * `length` - threshold length for the queue.
  * `restart_cooldown` - interval in seconds between buffer queue length checks.
  * `container` - list of labels to match for the action. Actions are performed on containers that match any of the label sets.
    * `labels` - one or more labels to match on the same container, i.e. the container must have all labels.
* `ingress` or `egress` - configuration for the input or output traffic of the buffer. Optional.
  * `action` - action to take when the time since the last input or output message exceeds the idle threshold. It can be `restart` or `stop`.
  * `idle` - threshold time in seconds since the last input or output message.
  * `restart_cooldown` - interval in seconds between ingress or egress idle checks.
  * `container` - list of labels to match for the action. Actions are performed on containers that match any of the label sets.
    * `labels` - one or more labels to match on the same container, i.e. the container must have all labels.

**Note**: For each buffer, at least one of the `queue`, `ingress`, or `egress` sections must be present.

You can find an example configuration file in the [samples](samples/pipeline_monitoring/config.yml) folder.

## Sample

The sample demonstrates how to start the watchdog service with an example pipeline to watch the buffer and restart the SDK client based on configuration and buffer state.

### Run

```bash
docker compose -f samples/pipeline_monitoring/docker-compose.yml up --build -d
```

### Check

After starting the pipeline, you can check the logs of the client container:
```bash
docker logs -f pipeline_monitoring-client-1
```
When the client stops processing messages for more than `egress.idle` seconds (see [config](samples/pipeline_monitoring/config.yml)) 
you will see the following logs in the client container, and the container itself will be restarted:
```
Traceback (most recent call last):
  File "/opt/savant/src/client.py", line 52, in <module>
    main()
  File "/opt/savant/src/client.py", line 37, in main
    time.sleep(sleep_duration)
KeyboardInterrupt
```

### Stop

```bash
docker compose -f samples/pipeline_monitoring/docker-compose.yml down
```

## Development

### Install requirements

```bash
make init-dev
```

### Format code

```bash
make reformat
```

### Run tests

```bash
make test
```
