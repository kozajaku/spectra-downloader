Virtual environment
===================

Before installation I really recommend setting up own Python virtual environment. Executing
following command will create new Python virtual environment in the current directory called ``env``::

    python3 -m venv env

Now you have to activate newly created virtual environment::


    source env/bin/activate

or

::

    . env/bin/activate

You can now proceed with installation. Every Python package necessary for tool execution will be downloaded directly
to your virtual environment. When you are done using the tool simply execute following command to deactivate virtual
environment::

    deactivate
