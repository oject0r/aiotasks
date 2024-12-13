import asyncio
import threading
import multiprocessing
import time
from typing import Callable, Any, Optional, Dict, Union, List, Tuple
from functools import wraps
import heapq


class TaskQueue:
    """
    Расширенная асинхронная очередь задач с поддержкой приоритетов, результатов,
    отмены задач, ожидания выполнения конкретных задач, группового запуска и т.д.
    """

    def __init__(self):
        self._queue = asyncio.PriorityQueue()
        self._tasks: Dict[int, Tuple[int, Callable, Optional[Callable], int, int, Optional[str]]] = {}
        self._task_id = 0
        self._results: Dict[int, Any] = {}
        self._workers = []

    async def _worker(self):
        """Worker coroutine to execute tasks from the queue."""
        while True:
            task_id, priority, coro, callback, retry, retry_interval, label = await self._queue.get()
            try:
                result = await coro()
                self._results[task_id] = result
                if callback:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
            except Exception as e:
                if retry > 0:
                    await asyncio.sleep(retry_interval)
                    await self.add_task(coro, callback, priority, retry - 1, retry_interval, label=label)
                else:
                    print(f"Task {task_id} failed after retries: {e}")
                    self._results[task_id] = e
            finally:
                # Задача завершена, удаляем из активных
                self._tasks.pop(task_id, None)
                self._queue.task_done()

    async def start(self, workers: int = 1):
        """
        Starts the task queue with the specified number of workers.
        :param workers: Number of worker coroutines to handle tasks.
        """
        self._workers = [asyncio.create_task(self._worker()) for _ in range(workers)]

    async def stop(self):
        """Stops all workers after the current tasks are completed."""
        await self._queue.join()
        for worker in self._workers:
            worker.cancel()

    async def add_task(self, coro: Callable[[], Any], callback: Optional[Callable[[Any], Any]] = None,
                       priority: int = 0, retry: int = 0, retry_interval: int = 0, label: Optional[str] = None) -> int:
        """
        Adds a new task to the queue.
        :param coro: An asynchronous callable representing the task.
        :param callback: Optional callback to handle the result of the task (sync or async).
        :param priority: Priority of the task (lower value means higher priority).
        :param retry: Number of retry attempts if the task fails.
        :param retry_interval: Interval (in seconds) between retries.
        :param label: An optional label to group or identify the task.
        :return: The ID of the task added.
        """
        self._task_id += 1
        task_id = self._task_id
        task_entry = (priority, coro, callback, retry, retry_interval, label)
        self._tasks[task_id] = task_entry
        await self._queue.put((task_id, *task_entry))
        return task_id

    async def add_task_with_label(self, coro: Callable[[], Any], label: str, callback: Optional[Callable[[Any], Any]] = None,
                                  priority: int = 0, retry: int = 0, retry_interval: int = 0) -> int:
        """
        Adds a task with a specified label.
        """
        return await self.add_task(coro, callback, priority, retry, retry_interval, label)

    def pending_tasks(self) -> int:
        """Returns the number of pending tasks in the queue."""
        return self._queue.qsize()

    def active_tasks(self) -> Dict[int, Callable]:
        """Returns a dictionary of active tasks: {task_id: (priority, coro, callback, retry, retry_interval, label)}."""
        return self._tasks

    def list_task_labels(self) -> List[str]:
        """List all labels of active tasks (excluding finished ones)."""
        labels = [t[-1] for t in self._tasks.values() if t[-1] is not None]
        return labels

    def count_tasks_by_label(self, label: str) -> int:
        """Count how many active tasks have a given label."""
        return sum(1 for t in self._tasks.values() if t[-1] == label)

    async def wait_for_task(self, task_id: int, timeout: Optional[float] = None) -> Any:
        """
        Wait for a specific task to complete and return its result.
        If task not found or never finishes, may timeout.
        """
        start_time = time.time()
        while True:
            if task_id in self._results:
                return self._results[task_id]
            if timeout is not None and (time.time() - start_time) > timeout:
                raise asyncio.TimeoutError("Waiting for task timed out.")
            await asyncio.sleep(0.1)

    def get_result(self, task_id: int) -> Any:
        """
        Get the result of a completed task if available.
        If the task failed, returns the exception.
        If the task is not completed yet, returns None.
        """
        return self._results.get(task_id, None)

    async def cancel_task(self, task_id: int) -> bool:
        """
        Attempts to cancel a task if it's still in the queue.
        Returns True if cancelled, False if already taken by a worker or not found.
        """
        # There is no straightforward way to remove from PriorityQueue.
        # We'll implement a hack: rebuild the queue without the cancelled task.
        # NOTE: This only works if the task wasn't taken by a worker yet.
        found = False
        new_queue = []
        while not self._queue.empty():
            item = await self._queue.get()
            if item[0] == task_id:
                found = True
                # do not re-put this task
                self._tasks.pop(task_id, None)
                self._queue.task_done()
            else:
                new_queue.append(item)
                self._queue.task_done()
        # rebuild queue
        for item in new_queue:
            await self._queue.put(item)
        return found

    def clear_results(self):
        """Clears all stored results of completed tasks."""
        self._results.clear()

    async def run_tasks_concurrently(self, coros: List[Callable[[], Any]], callback: Optional[Callable[[List[Any]], Any]] = None) -> List[Any]:
        """
        Run a list of coroutines concurrently using asyncio.gather.
        If callback is provided (sync or async), it's called with the list of results after all complete.
        """
        results = await asyncio.gather(*[c() for c in coros], return_exceptions=True)
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(results)
            else:
                callback(results)
        return results


class AioTasks:
    """
    Helper class to provide task scheduling decorators and functions.
    """

    @staticmethod
    def task(
        days: int = 0,
        months: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        callback: Optional[Union[Callable[[Any], Any], Callable[[Any], None]]] = None,
        use_threading: bool = False,
        use_multiprocessing: bool = False,
        run_once: bool = False
    ):
        """
        Decorator to schedule a coroutine or synchronous task to run periodically or once after a delay.

        :param days: Interval in days.
        :param months: Interval in months (approx. 30 days per month).
        :param hours: Interval in hours.
        :param minutes: Interval in minutes.
        :param seconds: Interval in seconds.
        :param milliseconds: Interval in milliseconds.
        :param callback: Optional callback to handle the result of the task (sync or async).
        :param use_threading: If True, run the task in a separate thread.
        :param use_multiprocessing: If True, run the task in a separate process.
        :param run_once: If True, run the task only once after the delay instead of periodically.
        """

        interval = (
            days * 86400 +
            months * 2592000 +  # Approximation: 30 days per month
            hours * 3600 +
            minutes * 60 +
            seconds +
            milliseconds / 1000
        )

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                def run_task():
                    if run_once:
                        time.sleep(interval)
                        result = func(*args, **kwargs)
                        if callback:
                            if asyncio.iscoroutinefunction(callback):
                                asyncio.run(callback(result))
                            else:
                                callback(result)
                    else:
                        while True:
                            result = func(*args, **kwargs)
                            if callback:
                                if asyncio.iscoroutinefunction(callback):
                                    asyncio.run(callback(result))
                                else:
                                    callback(result)
                            time.sleep(interval)

                if use_threading:
                    thread = threading.Thread(target=run_task, daemon=True)
                    thread.start()
                elif use_multiprocessing:
                    process = multiprocessing.Process(target=run_task, daemon=True)
                    process.start()
                else:
                    async def async_wrapper():
                        if run_once:
                            await asyncio.sleep(interval)
                            result = await func(*args, **kwargs)
                            if callback:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(result)
                                else:
                                    callback(result)
                        else:
                            while True:
                                result = await func(*args, **kwargs)
                                if callback:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(result)
                                    else:
                                        callback(result)
                                await asyncio.sleep(interval)

                    asyncio.create_task(async_wrapper())

            return wrapper
        return decorator

    @staticmethod
    async def gather(*coros: Callable[..., Any], return_exceptions=True, callback=None):
        """
        Runs multiple coroutines concurrently via asyncio.gather.
        If callback is provided, it is called with the list of results.
        """
        results = await asyncio.gather(*[c() for c in coros], return_exceptions=return_exceptions)
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(results)
            else:
                callback(results)
        return results

    @staticmethod
    async def run_once_at(coro: Callable[..., Any], run_time: float, callback: Optional[Callable[[Any], Any]] = None):
        """
        Schedules a coroutine to run at a specific Unix timestamp (run_time).
        """
        now = time.time()
        delay = run_time - now
        if delay > 0:
            await asyncio.sleep(delay)
        result = await coro()
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(result)
            else:
                callback(result)
        return result

    @staticmethod
    async def delayed_task(coro: Callable[..., Any], delay: float, callback: Optional[Callable[[Any], Any]] = None):
        """
        Runs a coroutine after a specified delay (in seconds).
        """
        await asyncio.sleep(delay)
        result = await coro()
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(result)
            else:
                callback(result)
        return result
