import zmq
import sys

from typing import Any, Tuple
from tornado import gen
from ipykernel.ipkernel import IPythonKernel


class AsyncGUIKernel(IPythonKernel):
    implementation = 'Async GUI'
    banner = (
        'Async GUI - Allow Comm messages to be passed '
        'when other cells are running.'
    )

    # Since this is not explicitly defined in the parent class
    comm_msg_types = [ 'comm_open', 'comm_msg', 'comm_close' ]

    def _parse_message(self, msg) -> Tuple[Any, dict]:
        """dispatch control requests"""
        idents, msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.deserialize(msg, content=True, copy=False)
            return (idents, msg)
        except:
            self.log.error("Invalid Message", exc_info=True)
            return

    @gen.coroutine
    def dispatch_shell(self, stream, msg: dict, idents):
        """dispatch shell requests"""
        # Set the parent message for side effects.
        self.set_parent(idents, msg)
        self._publish_status('busy')

        if self._aborting:
            self._send_abort_reply(stream, msg, idents)
            self._publish_status('idle')
            # flush to ensure reply is sent before
            # handling the next request
            stream.flush(zmq.POLLOUT)
            return

        msg_type = msg['header']['msg_type']

        # Print some info about this message and leave a '--->' marker, so it's
        # easier to trace visually the message chain when debugging.  Each
        # handler prints its message at the end.
        self.log.debug('\n*** MESSAGE TYPE:%s***', msg_type)
        self.log.debug('   Content: %s\n   --->\n   ', msg['content'])

        if not self.should_handle(stream, msg, idents):
            return

        handler = self.shell_handlers.get(msg_type, None)
        if handler is None:
            self.log.warning("Unknown message type: %r", msg_type)
        else:
            self.log.debug("%s: %s", msg_type, msg)
            try:
                self.pre_handler_hook()
            except Exception:
                self.log.debug("Unable to signal in pre_handler_hook:", exc_info=True)
            try:
                yield gen.maybe_future(handler(stream, idents, msg))
            except Exception:
                self.log.error("Exception in message handler:", exc_info=True)
            finally:
                try:
                    self.post_handler_hook()
                except Exception:
                    self.log.debug("Unable to signal in post_handler_hook:", exc_info=True)

        sys.stdout.flush()
        sys.stderr.flush()
        self._publish_status('idle')
        # flush to ensure reply is sent before
        # handling the next request
        stream.flush(zmq.POLLOUT)

    @gen.coroutine
    def dispatch_control(self, msg: dict, idents):
        self.log.debug("Control received: %s", msg)

        # Set the parent message for side effects.
        self.set_parent(idents, msg)
        self._publish_status('busy')
        if self._aborting:
            self._send_abort_reply(self.control_stream, msg, idents)
            self._publish_status('idle')
            return

        header = msg['header']
        msg_type = header['msg_type']

        handler = self.control_handlers.get(msg_type, None)
        if handler is None:
            self.log.error("UNKNOWN CONTROL MESSAGE TYPE: %r", msg_type)
        else:
            try:
                yield gen.maybe_future(handler(self.control_stream, idents, msg))
            except Exception:
                self.log.error("Exception in control handler:", exc_info=True)

        sys.stdout.flush()
        sys.stderr.flush()
        self._publish_status('idle')
        # flush to ensure reply is sent
        self.control_stream.flush(zmq.POLLOUT)

    def schedule_dispatch(self, priority, dispatch, *args):
        """
        Changes the schedule_dispatch dispatch method to
        always dispatch comm events.
        """

        # Only dispatch_shell messages have two args
        if len(args) == 2:
            stream, unparsed_msg = args
            indent, msg = self._parse_message(unparsed_msg)
            new_args = (stream, msg, indent)
        elif len(args) == 1:
            # One arg
            (unparsed_msg,) = args
            indent, msg = self._parse_message(unparsed_msg)
            new_args = (msg, indent)
        elif len(args) == 0:
            new_args = args

        if new_args and msg['header']['msg_type'] in self.comm_msg_types:
            return self.io_loop.add_callback(dispatch, *new_args)
        else:
            idx = next(self._message_counter)

            self.msg_queue.put_nowait(
                (
                    priority,
                    idx,
                    dispatch,
                    new_args,
                )
            )
            # ensure the eventloop wakes up
            self.io_loop.add_callback(lambda: None)

    def set_parent(self, ident, parent):
        # The last message sent will set what cell output
        # to use. We want to the awaiting future to print
        # it's own output, not the cell which the comm is
        # associated with.

        # Don't change the output if the message is from a comm
        #if parent['header']['msg_type'] not in self.comm_msg_types:
        super().set_parent(ident, parent)


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=AsyncGUIKernel)
