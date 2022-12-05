from time import sleep

from ontrack.utils.context import memcache_lock


def execute_task(task, method):
    """This task is used to pull_equity_eod_data from the website"""
    lock_id = f"{task.name}-lock"
    print(lock_id)
    print(task.app.oid)

    with memcache_lock(lock_id, task.app.oid) as acquired:
        if acquired:
            sleep(1)
            return method()

    return f"Task {task.name} is already being running by another worker."
