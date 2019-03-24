# ====================================================================================================================
#
# Script Name:      Dockerfile
#
# Author:           James Park, Linux Networks Ltd.
# Date:             24/03/19
#
# Description:      The following Dockerfile defines a simple image to run the microservice 'fetch-ext-ip-addr.py'.
#
# Run Information:  This image is intended to be run as part of the 'dns-updater' application stack.
#
# ====================================================================================================================


# Use an official Python runtime as a parent image.
FROM 		python:2.7-slim

# Set the working directory to /app.
WORKDIR 	/app

# Copy python dependencies into the container at /app.
COPY        requirements.txt /app

# Install any needed packages specified in requirements.txt.
RUN         pip install --trusted-host pypi.python.org -r requirements.txt

# Copy all python files into /app.
COPY        *.py /app

# Make port 80 available to the world outside this container.
EXPOSE 80

# Make all python files executable by users.
RUN         chmod u+x /app/*.py

# Define environment variables.
ENV         NAME fetch-ext-ip-addr
# Don't allow python to buffer it's output.
ENV         PYTHONUNBUFFERED True

# Run the executable.
CMD         ["./fetch-ext-ip-addr.py"]