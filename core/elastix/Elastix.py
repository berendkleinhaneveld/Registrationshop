"""
Elastix

:Authors:
    Berend Klein Haneveld
"""

import os
import multiprocessing

import itk


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

        fixedImage = itk.imread(command.fixedData, itk.F)
        movingImage = itk.imread(command.movingData, itk.F)

        parameterObject = itk.ParameterObject.New()
        parameterObject.AddParameterFile(command.transformation)

        kwargs = {
            "parameter_object": parameterObject,
            "log_to_console": False,
            "output_directory": command.outputFolder,
            "number_of_threads": numberOfCores,
        }
        if command.initialTransformation:
            kwargs[
                "initial_transform_parameter_file_name"
            ] = command.initialTransformation

        resultImage, resultTransformParameters = itk.elastix_registration_method(
            fixedImage, movingImage, **kwargs
        )
