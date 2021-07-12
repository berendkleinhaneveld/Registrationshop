"""
Elastix

:Authors:
    Berend Klein Haneveld
"""

import os
import sys
import subprocess
import multiprocessing


class Elastix(object):
    """
    Elastix

    Wrapper around the task-line tool Elastix.
    Inspired by pyelastix by Almar Klein. His project can be found
    at https://code.google.com/p/pirt/

    At the moment Elastix must be explicitly started and stopped in order to
    process tasks, but what might be a better idea is to just start
    processing tasks at the moment they are added and queue other incoming
    tasks. Implementing this would have to wait though on a working
    implementation of a task.
    """

    @classmethod
    def process(cls, command):
        """
        Process the given command.
        """
        assert command is not None
        assert command.isValid()

        # Ensure that the output folder actually exists before calling Elastix
        if not os.path.exists(command.outputFolder):
            os.makedirs(command.outputFolder)

        numberOfCores = multiprocessing.cpu_count()

        # Create Elastix command with the right parameters
        commands = [
            "elastix",
            "-m",
            command.movingData,
            "-f",
            command.fixedData,
            "-out",
            command.outputFolder,
            "-p",
            command.transformation,
            "-threads",
            str(numberOfCores),
        ]

        if command.initialTransformation:
            commands.append("-t0")
            commands.append(command.initialTransformation)

        # Try and call elastix
        try:
            proc = subprocess.Popen(commands, stdout=subprocess.PIPE)
            for line in iter(proc.stdout.readline, ""):
                # print line.rstrip()
                pass
        except Exception:
            print("Image registration failed with command:")
            print(commands)
            print("More detailed info:")
            print(sys.exc_info())
            raise
