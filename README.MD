# AioQueues

AioQueues is a lightweight Python library for creating and managing task queues with asyncio, threading, or multiprocessing. It supports:

- Asynchronous task scheduling
- Periodic task execution
- Prioritization and retries for tasks
- Mixed support for synchronous and asynchronous callbacks

## Features

- **Asynchronous Task Queues**: Create task queues with asyncio for high-performance, non-blocking operations.
- **Threading and Multiprocessing**: Run tasks in threads or processes for parallel execution.
- **Task Scheduling**: Schedule tasks to run periodically with flexible time intervals.
- **Retry Mechanism**: Automatically retry failed tasks with configurable intervals and limits.
- **Callbacks**: Supports both synchronous and asynchronous callbacks to handle task results.

## Installation

To install the library, clone this repository and include the `aioqueues.py` file in your project:

```bash
# Clone the repository
git clone https://github.com/oject0r/aioqueues.git

# Move aioqueues.py into your project folder
```

## Usage

### Example 1: Periodic Asynchronous Task
```python
from aioqueues import AioTasks
import asyncio

aiotasks = AioTasks()

async def async_callback(result):
    print(f"Async callback received result: {result}")

@aiotasks.task(seconds=2, callback=async_callback)
async def async_task():
    return "Async task completed"

async def main():
    await asyncio.sleep(10)

asyncio.run(main())
```

### Example 2: Synchronous Task with Threading
```python
from aioqueues import AioTasks
import time

aiotasks = AioTasks()

def sync_callback(result):
    print(f"Sync callback executed with result: {result}")

@aiotasks.task(seconds=3, use_threading=True, callback=sync_callback)
def sync_task():
    return "Sync result"

if __name__ == "__main__":
    sync_task()
    time.sleep(10)
```

### Example 3: Task Queue with Retry
```python
from aioqueues import TaskQueue
import asyncio

async def sample_task():
    print("Executing task...")
    return "Task result"

async def sample_callback(result):
    print(f"Task completed with result: {result}")

async def main():
    queue = TaskQueue()
    await queue.start(workers=2)
    await queue.add_task(sample_task, sample_callback, priority=1, retry=3, retry_interval=2)
    await asyncio.sleep(5)
    await queue.stop()

asyncio.run(main())
```

## Documentation

### AioTasks Class
- `@AioTasks.task(...)`
  - Parameters:
    - `days`, `months`, `hours`, `minutes`, `seconds`, `milliseconds`: Interval for task execution.
    - `callback`: Callback function (sync or async) to handle task results.
    - `use_threading`, `use_multiprocessing`: Specify the execution mode.

### TaskQueue Class
- `add_task(...)`
  - Parameters:
    - `coro`: Asynchronous task function.
    - `callback`: Callback function to handle task results.
    - `priority`: Priority of the task.
    - `retry`: Number of retry attempts.
    - `retry_interval`: Interval between retries.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

