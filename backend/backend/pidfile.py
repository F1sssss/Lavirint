import os
from pathlib import Path

from backend.logging import cli_logger
from backend.podesavanja import podesavanja


def exists():
    return os.path.exists(podesavanja.PIDFILE_PATH)


def ensure_path():
    try:
        Path(podesavanja.PIDFILE_PATH).parent.mkdir(mode=400, parents=True)
    except FileExistsError:
        pass


def append(new_pids):
    existing_pids = read_pids()
    pids = existing_pids + [new_pids] if isinstance(new_pids, int) else new_pids
    write_pids(pids)
    cli_logger.info('Appending PIDs to pidfile', extra={
        'pids': pids
    })


def write_pids(pids):
    with open(podesavanja.PIDFILE_PATH, 'w') as file:
        file.writelines(str(pid) + '\n' for pid in pids)


def append_current():
    append([os.getppid(), os.getpid()])


def remove_pids(pids_to_remove):
    current_pids = read_pids()

    for pid_to_remove in pids_to_remove:
        current_pids.remove(pid_to_remove)

    with open(podesavanja.PIDFILE_PATH, 'w') as file:
        file.writelines(str(pid) for pid in current_pids)


def remove(new_pid):
    remove_pids([new_pid])


def remove_current():
    remove_pids([os.getppid()])


def read_pids():
    try:
        with open(podesavanja.PIDFILE_PATH, 'r') as file:
            return [int(line) for line in file.readlines()]
    except FileNotFoundError:
        return []
