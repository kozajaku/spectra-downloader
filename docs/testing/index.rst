Testing
=======

To invoke tests simply execute following command which will automatically download necessary testing dependencies
and invoke tests::

    python3 setup.py test

If the dependencies are already installed in your environment, you can also directly use ``pytest`` command::

    pytest tests

Following testing dependencies are nowadays necessary to run tests:

- pytest

Tests require running connection in order to test the spectra downloading functionality. If you are not
currently connected to the Internet be prepared that some of **test_downloader.py** tests will fail.

.. toctree::
    :maxdepth: 2
