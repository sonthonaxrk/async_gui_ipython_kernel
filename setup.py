import os
import subprocess
from setuptools import setup
from setuptools.command.install import install


setup(
    name='async_gui_ipython_kernel',
    description=(
        'Allows GUI events to be processed '
        'while the IPython kernel is processing a cell'
    ),
    install_requires=[
        'ipykernel>=5.6.0'
    ],
    setup_requires=[
        'jupyter_client'
    ],
    version='0.0.0',
    py_modules=['async_gui_ipython_kernel'],
    data_files=[(
        'share/jupyter/kernels/async_gui_ipython_kernel',
        ['share/jupyter/kernels/spec/kernel.json']
    )],
)
