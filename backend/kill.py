import click
import psutil as psutil

from backend import pidfile
from backend.logging import cli_logger


@click.command('')
@click.option('-y', '--yes', 'assume_yes', is_flag=True)
def kill_if_exists(assume_yes):
    if not pidfile.exists():
        cli_logger.debug('PID file does not exist.')
        return

    try:
        pids = pidfile.read_pids()
    except ValueError:
        cli_logger.error('%s contents not correct format. Expected integer.')
        return

    new_pids = pids[:]
    for pid in pids:
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            cli_logger.info('Process with PID=%s does not exist. '
                                  'This is probably due to server shutting down unexpectedly.' % pid)
            new_pids.remove(pid)
            continue

        process_status = p.status()
        if process_status == psutil.STATUS_STOPPED:
            cli_logger.debug('Terminating process <PID: %s; Status: %s>' % (pid, process_status))
            p.kill()
            cli_logger.debug('Process <PID: %s; Status: %s> terminated' % (pid, process_status))
            new_pids.remove(pid)
            continue

        if not assume_yes:
            click.echo('PID file contains pid <PID: %s; Status: %s>. '
                       'The server is currently running or has stoped due to unexpected error.' % (pid, process_status))
            if not click.confirm('Do you want to stop that process?', default=True):
                continue

        try:
            cli_logger.debug('Terminating the process <PID: %s; Status: %s>' % (pid, process_status))
            p.terminate()
            p.wait(timeout=6)
            cli_logger.debug('Process %s terminated' % pid)
            new_pids.remove(pid)
            continue
        except psutil.TimeoutExpired:
            if click.confirm('Process with %s could not be terminated. '
                             'Do you want to force stop it?' % pid, default=True):
                p.kill()
                new_pids.remove(pid)
                cli_logger.warning('Process %s killed' % pid)
                continue

        cli_logger.info('Didn\'t do anything.')

    pidfile.write_pids(new_pids)


if __name__ == '__main__':
    kill_if_exists()
