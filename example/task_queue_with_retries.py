from aioqueues import TaskQueue
import asyncio

async def sample_task():
    # Task to be executed
    print("Executing task...")
    return "Task result"

async def sample_callback(result):
    # Callback function to process the task result
    print(f"Task completed with result: {result}")

async def main():
    queue = TaskQueue()
    await queue.start(workers=2)

    # Adding a task with priority and retry attempts
    await queue.add_task(sample_task, sample_callback, priority=1, retry=3, retry_interval=2)

    # Allow tasks to finish
    await asyncio.sleep(5)
    await queue.stop()

asyncio.run(main())
