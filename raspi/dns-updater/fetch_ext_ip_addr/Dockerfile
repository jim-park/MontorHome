# Use an official Python runtime as a parent image
FROM 		python:2.7-slim
#FROM        balenalib/raspberrypi3-alpine-python

# Set the working directory to /app
WORKDIR 	/app

# Copy python dependencies into the container at /app
COPY        requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN         pip install --trusted-host pypi.python.org -r requirements.txt

COPY        *.py /app

# Make port 80 available to the world outside this container
EXPOSE 80

RUN         chmod u+x *.py

# Define environment variable
ENV         NAME fetch-ext-ip-addr
ENV         PYTHONUNBUFFERED True

# Run the MH API
CMD         ["./fetch-ext-ip-addr.py"]
#CMD         ["/bin/bash"]