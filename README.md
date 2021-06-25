# Daemon library - used for daemonizing applications and related tools

## Instalation
### Directly pip
`pip3 install git+https://github.com/wholefolio/daemonliblib.git#egg=daemonlib`
### Via git clone
```
git clone https://github.com/wholefolio/applib
cd applib
```
## app.py - a tool for daemonizing and running applications
Given the config, the app will run separate processes passed in the config's processes path:
Example:
```
config = {"processes": ["incoming"]}
app = App(lock_file, MyApp, **config)
app.start()
```

Required arguments: 
* app class, that will be the actor 
* config - the config must contain at least the lock_file and the processes to run

## tools.py - useful tools for utilizing the app.py module.
This module contains functions to maintain an app instance and interact with it similarly to systemd:
* start - start an application daemonizing it
* stop - stop an existing application
* restart - stop/start the app
* status - check if it's running and the pids of the processes
