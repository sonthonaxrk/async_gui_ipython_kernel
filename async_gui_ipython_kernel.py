import logging
import zmq
import sys

from typing import Any, Tuple
from tornado import gen
from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelapp import IPKernelApp
from ipykernel import kernelspec
from ipykernel.kernelspec import (
    InstallIPythonKernelSpecApp,
    make_ipkernel_cmd, _is_debugpy_available)
from traitlets import Unicode

from argparse import ArgumentParser
from pathlib import Path



class AsyncGUIKernel(IPythonKernel):
    implementation = 'Async GUI'
    banner = (
        'Async GUI - Allow Comm messages to be passed '
        'when other cells are running.'
    )

    # Since this is not explicitly defined in the parent class
    comm_msg_types = [ 'comm_msg' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = self.log.getChild('AsyncGUIKernel')
        self.log.setLevel(logging.INFO)


    def _parse_message(self, msg) -> Tuple[Any, dict]:
        """dispatch control requests"""
        idents, msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.deserialize(msg, content=False, copy=False)
            return (idents, msg)
        except:
            self.log.error("Invalid Message", exc_info=True)
            return


    def schedule_dispatch(self, dispatch, *args):
        """
        Changes the schedule_dispatch dispatch method to
        always dispatch comm events.
        """

        idx = next(self._message_counter)
        indent, msg = self._parse_message(args[0])
        msg_type = (msg.get('header', dict()).get('msg_type', ''))

        if msg_type in self.comm_msg_types:
            return self.io_loop.add_callback(dispatch, *args)

        self.msg_queue.put_nowait(
            (
                idx,
                dispatch,
                args,
            )
        )

        # ensure the eventloop wakes up
        self.io_loop.add_callback(lambda: None)


    def set_parent(self, ident, parent, channel="shell"):
        """Overridden from parent to tell the display hook and output streams
        about the parent message.
        """

        # Don't change the output if the message is from a comm
        #if parent['header']['msg_type'] not in self.comm_msg_types:
        if parent['header']['msg_type'] not in self.comm_msg_types:
            super().set_parent(ident, parent, channel)
            if channel == "shell":
                self.shell.set_parent(parent)


default_display_name = "Async GUI Python %i (asyng_gui_ipython_kernel)" % sys.version_info[0]


def custom_get_kernel_dict(extra_arguments=None):
    return {
        "argv": make_ipkernel_cmd('async_gui_ipython_kernel', extra_arguments=extra_arguments),
        "display_name": default_display_name,
        "language": "python",
        "metadata": {"debugger": _is_debugpy_available}}

# Monkey patching `get_kernel_dict` to use custom `mod``
kernelspec.get_kernel_dict = custom_get_kernel_dict


class InstallAsyncGUIKernelSpecApp(InstallIPythonKernelSpecApp):
    name = Unicode("async-gui-ipython-kernel-install")

    def initialize(self, argv=None):
        super().initialize(argv)

        default_argv = {
            '--name': 'async-gui-' + kernelspec.KERNEL_NAME,
            '--display-name': default_display_name}

        for k, v in default_argv.items():
            if k not in self.argv:
                self.argv += [k, v]


class AsyncGUIKernelApp(IPKernelApp):
    name = Unicode('async-gui-ipython-kernel')

    subcommands = {
        "install": (
            "async_gui_ipython_kernel.InstallAsyncGUIKernelSpecApp",
            "Install the IPython kernel")}


if __name__ == '__main__':
    AsyncGUIKernelApp.launch_instance(kernel_class = AsyncGUIKernel)
