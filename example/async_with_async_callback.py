from aioqueues import AioTasks
import asyncio

aiotasks = AioTasks()

async def async_callback(result):
    # Callback function that receives the result of the task
    print(f"Async callback received result: {result}")

@aiotasks.task(seconds=2, callback=async_callback)
async def async_task():
    # Periodic asynchronous task
    return "Async task completed"

async def main():
    # Running the asynchronous periodic task
    await asyncio.sleep(10)  # Allow the task to run multiple iterations

asyncio.run(main())
