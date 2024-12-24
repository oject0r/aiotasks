# AioQueues

**AioQueues** is a robust Python library designed for creating and managing task queues with support for asyncio, threading, and multiprocessing. It offers advanced features like:

- Asynchronous task scheduling and execution.
- Periodic task execution with customizable intervals.
- Task prioritization, retries, and result management.
- Mixed support for synchronous and asynchronous callbacks.
- Task labeling, cancellation, and concurrent execution.

## Features

- **Asynchronous Task Queues**: Use asyncio for high-performance, non-blocking task management.
- **Threading and Multiprocessing**: Run tasks in parallel using threads or processes.
- **Task Scheduling**: Schedule periodic or delayed task execution with flexible time intervals.
- **Task Management**: Track, cancel, and retrieve results for individual tasks.
- **Retry Mechanism**: Automatically retry failed tasks with configurable intervals and limits.
- **Task Labels**: Group or identify tasks with custom labels for better management.
- **Callbacks**: Supports synchronous and asynchronous callbacks for handling task results.
- **Concurrent Execution**: Run multiple coroutines concurrently with optional post-execution callbacks.

## Installation

Clone this repository and include the `aioqueues.py` file in your project:

```bash
# Clone the repository
git clone https://github.com/oject0r/aiotasks.git

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

### Example 3: Task Queue with Retry and Results Management

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
    
    # Add task with retry
    task_id = await queue.add_task(sample_task, sample_callback, priority=1, retry=3, retry_interval=2)
    
    # Wait for task completion and get the result
    result = await queue.wait_for_task(task_id)
    print(f"Task {task_id} completed with result: {result}")
    
    # Stop the queue
    await queue.stop()

asyncio.run(main())
```

### Example 4: Concurrent Execution of Multiple Tasks

```python
from aioqueues import TaskQueue
import asyncio

async def task1():
    await asyncio.sleep(1)
    return "Result 1"

async def task2():
    await asyncio.sleep(2)
    return "Result 2"

async def result_callback(results):
    print(f"All tasks completed with results: {results}")

async def main():
    queue = TaskQueue()
    await queue.start(workers=2)
    
    # Run tasks concurrently
    await queue.run_tasks_concurrently([task1, task2], result_callback)
    
    await queue.stop()

asyncio.run(main())
```

## Documentation

### **AioTasks Class**

#### `@AioTasks.task(...)`

Decorator for scheduling tasks.

- **Parameters**:
  - `days`, `months`, `hours`, `minutes`, `seconds`, `milliseconds`: Interval for task execution.
  - `callback`: A synchronous or asynchronous callback function to handle task results.
  - `use_threading`, `use_multiprocessing`: Specify the execution mode.
  - `run_once`: If `True`, the task runs only once after the specified delay.

#### `AioTasks.gather(...)`
Run multiple coroutines concurrently with `asyncio.gather` and optional post-execution callback.

#### `AioTasks.run_once_at(coro, run_time, callback=None)`
Schedule a coroutine to run at a specific Unix timestamp.

#### `AioTasks.delayed_task(coro, delay, callback=None)`
Run a coroutine after a specified delay.

---

### **TaskQueue Class**

#### `add_task(...)`
Add a new task to the queue.

- **Parameters**:
  - `coro`: Asynchronous task function.
  - `callback`: Callback function to handle task results.
  - `priority`: Priority of the task (lower value = higher priority).
  - `retry`: Number of retry attempts for the task.
  - `retry_interval`: Interval between retries.
  - `label`: Optional label for task grouping or identification.

#### `add_task_with_label(...)`
Add a task with a specific label for easy grouping.

#### `run_tasks_concurrently(...)`
Run multiple coroutines concurrently with optional post-execution callback.

#### `wait_for_task(task_id, timeout=None)`
Wait for a specific task to complete and return its result.

#### `get_result(task_id)`
Retrieve the result of a completed task.

#### `cancel_task(task_id)`
Attempt to cancel a task if it has not been taken by a worker.

#### `list_task_labels()`
List all labels of currently active tasks.

#### `count_tasks_by_label(label)`
Count the number of active tasks with a specific label.

#### `clear_results()`
Clear all stored results of completed tasks.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
