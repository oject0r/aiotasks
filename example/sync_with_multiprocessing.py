from aioqueues import AioTasks
import time

aiotasks = AioTasks()

def sync_task():
    # Task executed in a separate process
    print("Executing task in multiprocessing")
    return "Multiprocessing result"

def sync_callback(result):
    # Callback function for the task
    print(f"Callback for multiprocessing received result: {result}")

@aiotasks.task(seconds=6, use_multiprocessing=True, callback=sync_callback)
def periodic_multiprocessing_task():
    return sync_task()

if __name__ == "__main__":
    # Running the task in a separate process
    periodic_multiprocessing_task()
    time.sleep(15)  # Allow the task to run multiple iterations
