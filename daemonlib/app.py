"""App class to daemonize a python application."""
import sys
import os
import atexit
import logging
import psutil
from configparser import ConfigParser
from multiprocessing import Process
from time import sleep


def read_config(config):
    """Read the configuration file and return a dict with the config."""
    parser = ConfigParser()
    parser.read(config)
    config = {}
    for section_name in parser.sections():
        config[section_name] = {}
        for name, value in parser.items(section_name):
            config[section_name][name] = value
    return config


class App:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method.
    """

    def __init__(self, pidfile, app_class, daemonize=True, **config):
        """Assign the pidfile and config."""
        self.pidfile = pidfile
        self.app_class = app_class
        self.config = config

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()
        # write pidfile
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')
        atexit.register(self.delpid)

    def delpid(self):
        """Delete the lockfile at exit."""
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:
                pids = pf.readlines()
        except IOError:
            pids = None
        if pids:
            print("Lockfile {0} already exists, processes: {1}. Checking pids".format(self.pidfile, pids))
            for pid in pids:
                if psutil.pid_exists(int(pid)):
                    sys.stderr.write("Found existing process with PID: {}. Exiting!!!\n".format(pid))
                    sys.exit(1)
            print("Processes are non-existing - removing the lockfile")
            self.delpid()
        # Start the daemon
        daemon = self.config.get("daemon", True)
        if daemon:
            self.daemonize()
        self.run()

    def run(self):
        """Run the functions passed in as kwargs."""
        logger = logging.getLogger()
        processes_dict = self.config.get("processes")

        if not processes_dict:
            msg = "The dictionary of processes is missing from config!\n"
            sys.stderr.write(msg)
        # Initiate the processes
        manager = self.app_class(**self.config)
        restart_counters = {}
        for name, proc in processes_dict.items():
            msg = "Starting process {}\n".format(name)
            sys.stdout.write(msg)
            processes_dict[name] = Process(target=getattr(manager, name),
                                           name=name)
            processes_dict[name].start()
            restart_counters[name] = 0
            with open(self.pidfile, "a+") as f:
                f.write("{}\n".format(processes_dict[name].pid))        
        restart_limit = self.config.get("restart_limit", 5)
        exit = False
        while True:
            if exit:
                # Exit flag set - we are closing all processes
                for name, proc in processes_dict.items():
                    proc.terminate()
                sys.exit(1)
            logger.debug("Checking for dead processes")
            # Loop looking for dead processes
            for name, proc in processes_dict.items():
                if not proc.is_alive():
                    count = restart_counters[name]
                    if count > restart_limit:
                        logger.critical(f"Restart limit reached for {name} - shutting down")
                        exit = True
                        break
                    msg = "{'message':'Process %s has died. Restart try: %s)'}" % (name, count)
                    logger.critical(msg)
                    processes_dict[name] = Process(target=getattr(manager,
                                                                  name),
                                                   name=name)
                    processes_dict[name].start()
                    restart_counters[name] += 1
                sleep(5)
