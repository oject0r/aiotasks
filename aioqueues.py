import asyncio
import threading
import multiprocessing
import time
from typing import Callable, Any, Optional, Dict, Union
from functools import wraps

class TaskQueue:
	"""
	A lightweight asynchronous task queue for local use.
	Allows scheduling, task prioritization, retrying, and monitoring task execution.
	"""
	def __init__(self):
		"""Initializes an empty task queue."""
		self._queue = asyncio.PriorityQueue()
		self._tasks: Dict[int, asyncio.Task] = {}
		self._task_id = 0

	async def _worker(self):
		"""Worker coroutine to execute tasks from the queue."""
		while True:
			task_id, priority, coro, callback, retry, retry_interval = await self._queue.get()
			try:
				result = await coro()
				if callback:
					if asyncio.iscoroutinefunction(callback):
						await callback(result)
					else:
						callback(result)
			except Exception as e:
				if retry > 0:
					await asyncio.sleep(retry_interval)
					await self.add_task(coro, callback, priority, retry - 1, retry_interval)
				else:
					print(f"Task {task_id} failed after retries: {e}")
			finally:
				del self._tasks[task_id]
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

	async def add_task(self, coro: Callable[[], Any], callback: Optional[Callable[[Any], Any]] = None, priority: int = 0, retry: int = 0, retry_interval: int = 0):
		"""
		Adds a new task to the queue.

		:param coro: An asynchronous callable representing the task.
		:param callback: Optional callback to handle the result of the task (sync or async).
		:param priority: Priority of the task (lower value means higher priority).
		:param retry: Number of retry attempts if the task fails.
		:param retry_interval: Interval (in seconds) between retries.
		:return: The ID of the task added.
		"""
		self._task_id += 1
		task_id = self._task_id
		task_entry = (priority, coro, callback, retry, retry_interval)
		self._tasks[task_id] = task_entry
		await self._queue.put((task_id, *task_entry))
		return task_id

	def pending_tasks(self) -> int:
		"""Returns the number of pending tasks in the queue."""
		return self._queue.qsize()

	def active_tasks(self) -> Dict[int, Callable]:
		"""Returns a dictionary of active tasks."""
		return self._tasks

class AioTasks:
	"""
	Helper class to provide task scheduling decorators.
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
	):
		"""
		Decorator to schedule a coroutine or synchronous task to run periodically.

		:param days: Interval in days.
		:param months: Interval in months (approx. 30 days per month).
		:param hours: Interval in hours.
		:param minutes: Interval in minutes.
		:param seconds: Interval in seconds.
		:param milliseconds: Interval in milliseconds.
		:param callback: Optional callback to handle the result of the task (sync or async).
		:param use_threading: If True, run the task in a separate thread.
		:param use_multiprocessing: If True, run the task in a separate process.
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

# # Example usage
# if __name__ == "__main__":
# 	aiotasks = AioTasks()
#
# 	def sync_task():
# 		print("Sync task executed")
# 		return "Sync result"
#
# 	def callback(result):
# 		print(f"Callback executed with result: {result}")
#
# 	@aiotasks.task(seconds=5, use_threading=True, callback=callback)
# 	def periodic_sync_threaded_task():
# 		return sync_task()
#
# 	async def main():
# 		# Start periodic sync task in a thread
# 		periodic_sync_threaded_task()
# 		await asyncio.sleep(20)  # Run the event loop for 20 seconds to observe execution
#
# 	asyncio.run(main())
