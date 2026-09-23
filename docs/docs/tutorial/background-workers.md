# Background workers

FastID keeps durable background work outside the FastAPI request process. Webhook delivery and CPU-heavy jobs use
separate worker lanes, but both lanes can run under one worker command and from the same application image.

This distinction matters for tasks such as PDF generation, image processing, compression, document conversion, and
large imports. An `async` function does not make CPU-bound work non-blocking: running that code in the API process can
still monopolize the interpreter or its CPU allocation and make HTTP latency unpredictable. FastID executes trusted CPU
handlers in spawned child processes so that the event loop remains responsive and a timed-out job process can be
terminated.

## Worker lanes

| Lane | Responsibility | Execution model | Default concurrency |
| --- | --- | --- | --- |
| `webhooks` | Claim and deliver durable webhook records | Async network I/O in the worker process | `10` |
| `cpu` | Claim durable CPU jobs and run registered handlers | Spawned child processes | `1` |

The lanes share PostgreSQL as their durable source of truth, but have independent concurrency controls. CPU jobs have
leases, ownership tokens, heartbeats, execution timeouts, retries, and terminal failure state. If a worker disappears,
another worker may reclaim the job after its lease expires. A stale worker cannot commit a result after ownership has
moved to another worker.

The CPU infrastructure does not register application-specific handlers by default. Before enqueueing a job kind, add a
top-level, importable handler to the trusted `CPUHandlerRegistry` created in `fastid.background.runner`. Do not accept a
module path or arbitrary callable name from an API request: job kinds must map to code chosen by the application.

## Running locally

With the project environment and `.env` loaded, select one or both lanes:

```console
poetry run python -m fastid.background.runner --queues webhooks
poetry run python -m fastid.background.runner --queues cpu
poetry run python -m fastid.background.runner --queues webhooks,cpu
```

The existing command below remains a webhook-only compatibility wrapper:

```console
poetry run python -m fastid.webhooks.worker
```

Stop signals initiate a graceful drain. The worker stops claiming new work, waits for in-flight work up to the configured
drain timeout, and then cancels or terminates remaining execution. Durable leases allow unfinished work to be recovered.

## Deployment options

### Separate API and worker containers

This is the default Compose layout and the safest general-purpose choice. `fastid-app` handles HTTP traffic and
`fastid-webhook-worker` runs only the webhook lane. Both services use the same image; the worker service changes only the
entrypoint.

Use a second worker service when CPU load needs an independent CPU or memory limit:

```yaml
services:
  fastid-cpu-worker:
    image: everysoftware/fastid:latest
    env_file: .env
    entrypoint: ["python", "-m", "fastid.background.runner", "--queues", "cpu"]
    restart: unless-stopped
```

This gives the strongest failure isolation and lets webhook I/O and CPU work scale independently. It does add one
long-running container for each independently scaled role.

### One external worker for both lanes

For a small installation, one worker process can service webhook and CPU queues together:

```yaml
services:
  fastid-worker:
    image: everysoftware/fastid:latest
    env_file: .env
    entrypoint: ["python", "-m", "fastid.background.runner", "--queues", "webhooks,cpu"]
    restart: unless-stopped
```

This keeps the API isolated from background failures while avoiding separate webhook and CPU worker containers. The
webhook coroutine and the CPU coordinator coexist in one parent process; actual CPU handlers still run in child
processes. A parent-worker crash temporarily pauses both lanes, and both lanes share the container's CPU and memory
limits, so this mode is best for modest traffic.

### One application container

FastID can run without a separate worker container, but the API server and worker should still be separate operating
system processes. Put both commands under a real process supervisor such as `s6-overlay`, `supervisord`, or systemd:

```text
process 1: uvicorn fastid.main:app ...
process 2: python -m fastid.background.runner --queues webhooks,cpu
```

The supervisor must forward termination signals to both processes, restart a failed child, reap child processes, and
wait for graceful shutdown. Do not launch the durable worker as an untracked FastAPI lifespan task: every API replica
would start another worker, CPU pressure would directly compete with request handling, and an API restart would also
interrupt all background coordination.

This is the smallest application deployment footprint, but it is one container with multiple processes rather than one
process. PostgreSQL and Redis are still external dependencies, whether hosted services or separate containers. Give the
container enough headroom for the API, parent worker, and every concurrent CPU child.

### Fully split roles

At higher load, run three roles from the same image:

1. API containers handle requests only.
2. Webhook workers handle network-bound delivery only.
3. CPU workers handle CPU- and memory-bound jobs only.

This costs another service definition, but provides independent scaling, resource limits, deploys, and failure domains.
For example, a PDF spike can consume the CPU-worker quota without starving login requests or webhook delivery.

## Configuration and capacity

CPU settings use the `FASTID_CPU_WORKER_` prefix:

| Variable | Default | Meaning |
| --- | ---: | --- |
| `FASTID_CPU_WORKER_CONCURRENCY` | `1` | Maximum simultaneous CPU child processes |
| `FASTID_CPU_WORKER_BATCH_SIZE` | `1` | Maximum jobs claimed per poll, additionally capped by free concurrency |
| `FASTID_CPU_WORKER_POLL_SECONDS` | `1.0` | Idle polling interval |
| `FASTID_CPU_WORKER_LEASE_SECONDS` | `60` | Claim lifetime without a successful heartbeat |
| `FASTID_CPU_WORKER_HEARTBEAT_SECONDS` | `15.0` | Lease refresh interval; must be shorter than the lease |
| `FASTID_CPU_WORKER_TIMEOUT_SECONDS` | `300.0` | Maximum execution time for one handler |
| `FASTID_CPU_WORKER_DRAIN_TIMEOUT_SECONDS` | `30.0` | Graceful shutdown wait for in-flight jobs |
| `FASTID_CPU_WORKER_RETRY_DELAYS_SECONDS` | `5,30,300` | Delays used by successive retries |

Start CPU concurrency at one on a small host. Increase it only after measuring CPU saturation, resident memory per child,
job duration, API latency, and database pressure. For memory-heavy PDF or image jobs, the safe concurrency can be lower
than the number of CPU cores. Set container CPU and memory limits so an unexpectedly large input cannot exhaust the host.

Each process has its own SQLAlchemy pool. The database settings are `FASTID_DB_POOL_SIZE`,
`FASTID_DB_MAX_OVERFLOW`, `FASTID_DB_POOL_TIMEOUT`, and `FASTID_DB_POOL_RECYCLE`. Account for every API and worker process
when calculating the maximum number of PostgreSQL connections; defaults intended for one process multiply quickly when
roles are replicated.

## Designing CPU jobs

Keep the durable payload small and serializable. Store source files and generated artifacts in object or file storage,
then put stable references, checksums, and options in the job payload. Passing multi-megabyte documents through a JSON
database column makes claims, retries, backups, and observability unnecessarily expensive.

Handlers should be deterministic where practical and safe to run more than once. Leases prevent stale commits, but they
cannot undo an external side effect that completed immediately before a process crash. Use a job ID or business key for
idempotent storage paths and downstream requests.

Validate size, page count, format, and decompression limits before expensive processing. Treat PDF renderers, office
converters, image libraries, and archive tools as parsers for untrusted input: keep dependencies patched, apply execution
timeouts and memory limits, and consider a more restrictive sandbox when the files come from untrusted users.

Record only compact result metadata in PostgreSQL, such as an artifact key, byte size, checksum, page count, and content
type. Serve the artifact from storage rather than returning it through the job row.
