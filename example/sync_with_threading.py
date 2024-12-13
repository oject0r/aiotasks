from aioqueues import AioTasks
import time

aiotasks = AioTasks()

def sync_callback(result):
    # Callback function for the synchronous task
    print(f"Sync callback executed with result: {result}")

@aiotasks.task(seconds=3, use_threading=True, callback=sync_callback)
def sync_task():
    # Periodic synchronous task
    print("Sync task executed")
    return "Sync result"

if __name__ == "__main__":
    # Running the synchronous task in a separate thread
    sync_task()
    time.sleep(10)  # Allow the task to run multiple iterations
