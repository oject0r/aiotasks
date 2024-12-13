from aioqueues import AioTasks
import asyncio

aiotasks = AioTasks()

@aiotasks.task(seconds=5)
async def task_1():
    # First periodic task
    print("Task 1 executed")

@aiotasks.task(seconds=8)
async def task_2():
    # Second periodic task
    print("Task 2 executed")

async def main():
    # Running multiple tasks with different intervals
    await asyncio.sleep(20)  # Observe the execution

asyncio.run(main())
