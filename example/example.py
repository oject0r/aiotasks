from aioqueues import *
import asyncio

# Example usage of extended functionalities
if __name__ == "__main__":
    async def example_coro():
        await asyncio.sleep(1)
        return "done"

    async def main():
        q = TaskQueue()
        await q.start(workers=2)

        # Add a few tasks
        t1 = await q.add_task(example_coro)
        t2 = await q.add_task(example_coro, label="group1")

        # Wait for a specific task
        result_t1 = await q.wait_for_task(t1)
        print("Result of t1:", result_t1)

        # Check results directly
        print("Result of t2:", q.get_result(t2))

        # Run multiple coroutines concurrently
        results = await q.run_tasks_concurrently([example_coro, example_coro])
        print("Concurrent results:", results)

        # Cancel a task (demonstration)
        t3 = await q.add_task(example_coro, label="group2")
        cancelled = await q.cancel_task(t3)
        print("Task t3 cancelled:", cancelled)

        await q.stop()

    asyncio.run(main())

    # AioTasks example
    async def print_hello():
        print("Hello after delay")
        return "Hello"

    # Run once at a specific time (5 seconds from now)
    future_time = time.time() + 5
    asyncio.run(AioTasks.run_once_at(print_hello, future_time))

    # Delayed task
    asyncio.run(AioTasks.delayed_task(print_hello, 3))