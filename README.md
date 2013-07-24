stream-graph
============

accept time series of stream gauge images and generate hydrograph

Dependencies to install before running
======================================

    sudo apt-get install python-opencv ipython-notebook python-matplotlib python-numpy python-scipy

How to run inside LXC
=====================

    ipython notebook --ip 0.0.0.0 --no-browser --pylab=inline

NOTE: Do *NOT* run this on your own machine using --ip 0.0.0.0 since
that will expose your machine to security vulnerabilities. Only use
that inside your LXC container.
