# Async GUI IPython Kernel

This enables the IPython kernel to receive `Comm` events while waiting for cells.

Currently, the IPython kernel will only process one message at a time. Including Comm events that are naturally asynchronous. This means you are currently unable to await changes in your `ipywidgets`. This package tries to rectify that.

Being able to wait on user input in Jupyter opens up possibilities for building interfaces. Without this, Jupyter widgets are quite limited as input tools.


![Demo](https://gist.githubusercontent.com/sonthonaxrk/01a0428bd318e477686d21a8b3135534/raw/7dcd0601bab46f291821023bbe3c69fdc4477407/asnyc_widget.gif)

## Quickstart

I am hesitant to publish this to PyPi because this is a hack, and I would like to patch the Kernel, so I can do this without that as much ugly method overriding.

    $ pip install pip install git+git://github.com/sonthonaxrk/async_gui_ipython_kernel.git#egg=async_gui_ipython_kernel

This will automatically install the kernel.
