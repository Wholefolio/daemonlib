import os
import sys
import subprocess
import re
from signal import SIGTERM

from daemonlib.app import App


def check_lock_file(config):
    """Check the config for a lockfile location."""
    if not config.get('lock_file'):
        sys.stderr.write("Missing lock file from config\n")
        sys.exit(1)


def start(app_name, app_class, config):
    """Start the daemon."""
    check_lock_file(config)
    app = App(config['lock_file'], app_class, **config)
    sys.stderr.write("Starting daemon {}...\n".format(app_name))
    try:
        app.start()
    except PermissionError as e:
        sys.stderr.write("Start failed: {}\n".format(e))
        sys.exit(1)
    except OSError as err:
        sys.stderr.write("Error during start: {}\n".format(err))
        stop()


def stop(config):
    """Stop the daemon."""
    check_lock_file(config)
    sys.stderr.write("Stopping daemon...\n")
    try:
        with open(config["lock_file"], 'r') as f:
            for line in f.readlines():
                # If it excepts than the process is already dead
                try:
                    os.kill(int(line.strip()), SIGTERM)
                except ProcessLookupError:
                    pass
                except PermissionError:
                    sys.stderr.write("Stop failed - permission denied.\n")
                    sys.exit(1)
        try:
            os.remove(config["lock_file"])
            if config.get("sock_file"):
                os.remove(config["sock_file"])
        except PermissionError:
            sys.stderr.write("Stop failed - permission denied.\n")
            sys.exit(1)
    except FileNotFoundError:
        sys.stderr.write("Lockfile not found. Is the daemon running?\n")


def status(app_name, config):
    """Show status of the daemon."""
    check_lock_file(config)
    try:
        with open(config["lock_file"], 'r') as f:
            pids = f.readlines()
            ms = "Daemon is running with these PIDs:\n{}".format("".join(pids))
            sys.stderr.write(ms)
    except FileNotFoundError:
        output = subprocess.check_output(['ps', 'aux']).decode()
        check = None
        pattern = re.compile('{}\.py'.format(app_name))
        match = pattern.findall(output)
        if len(match) > 2:
            check = "{} daemon is running.".format(app_name)
        if check:
            sys.stderr.write("{} NO LOCKFILE FOUND.\n".format(check))
        else:
            sys.stderr.write("{} is not running.\n".format(app_name.upper()))


def main(app_name, app_class, config):
    """."""
    usage = "USAGE: {}.py start|stop|restart|status\n".format(app_name)
    if len(sys.argv) == 1:
        sys.stderr.write(usage)
        sys.exit(1)
    options = ['start', 'stop', 'restart', 'status']
    if sys.argv[1] not in options:
        sys.stderr.write(usage)
        sys.exit(1)
    if sys.argv[1] == 'start':
        start(app_name, app_class, config)
    elif sys.argv[1] == 'stop':
        stop(config)
    elif sys.argv[1] == 'restart':
        stop(config)
        start(app_name, app_class, config)
    else:
        status(app_name, config)
