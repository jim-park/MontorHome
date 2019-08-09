# Use an official Python runtime as a parent image
FROM    python:2.7-slim

# Define environment variable
ENV     NAME    daq
ENV     PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR     /app

# Install any needed packages specified in requirements.txt
COPY    requirements.txt /app
RUN     pip install --trusted-host pypi.python.org -r requirements.txt

COPY    *.py /app/
RUN     chmod 775 /app/*.py

# Set proxy server, replace host:port with values for your servers.
CMD     ["./daq.py"]
