
""" Logging module for the voice control

This module keeps the global variable 'vc_logger' that other modules can import and use to log their activities.
Before this variable can b e used, the init_logger method must be called. This should be done in initializing the main function.

"""

import datetime
import logging

level_dict = {"error":logging.ERROR,"warning":logging.WARN,"info":logging.INFO, "debug":logging.DEBUG, "notset":logging.NOTSET}

def init_logger(level = "info", verbose=False):
    level = level_dict[level]
    vc_logger = logging.getLogger("vc_logger")
    vc_logger.setLevel(level)

    if verbose:
        console = logging.StreamHandler()
        console.setLevel(level)

        c_formatter = logging.Formatter('%(asctime)-15s %(message)s')
        console.setFormatter(c_formatter)

        vc_logger.addHandler(console)

    log_dir = 'logs/'
    log_name = datetime.datetime.now().strftime('log_voice_control_%Y_%m_%d')
    log_name = log_dir + log_name

    # Gets a logging file for this session (a new log every day)
    f_handler = logging.FileHandler(log_name)
    f_handler.setLevel(level)

    f_formatter = logging.Formatter('%(asctime)-15s %(levelno)s %(threadName)-10s %(funcName)-10s %(message)s')
    f_handler.setFormatter(f_formatter)

    vc_logger.addHandler(f_handler)

    # Define a hello message and a separator for separating different program executions in the logging file
    hello_msg = datetime.datetime.now().strftime('----------%H:%M:%S----------\n')
    sep = '-----------------------------\n'
    hello_msg = sep + hello_msg + sep

    # Append to the logging file every time the program is executed
    with open(log_name, 'a') as f:
        f.write(hello_msg)
