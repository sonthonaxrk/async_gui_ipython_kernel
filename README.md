# Async GUI IPython Kernel

This enables the IPython kernel to receive `Comm` events while waiting for cells.

Currently, the IPython kernel will only process one message at a time. Including Comm events that are naturally asynchronous. This means you are currently unable to await changes in your `ipywidgets`. If you do, the `await` statement will hang indefinitely.


Being able to wait on user input in Jupyter opens up possibilities for building interfaces. For example, in the GIF below, you can `await` on a GUI that takes a series of inputs. 


![Demo](https://gist.githubusercontent.com/sonthonaxrk/01a0428bd318e477686d21a8b3135534/raw/7dcd0601bab46f291821023bbe3c69fdc4477407/asnyc_widget.gif)



[Example Async Widget](https://gist.githubusercontent.com/sonthonaxrk/cf805531e9c362ae16722f6e9439814a/raw/5bbabeed1e0afec91b35eca47264e96308991136/ipywidget_async.py)

## Quickstart

    $ pip install pip install git+git://github.com/sonthonaxrk/async_gui_ipython_kernel.git#egg=async_gui_ipython_kernel
    
Make sure to set your kernel to 'Async GUI kernel'.


## Disclaimer

This is just an untested hack that could be useful.
