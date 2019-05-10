# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Copy the current directory contents into the container at /app
#ADD . /app

# Set the working directory to /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y install nginx supervisor gcc

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
COPY *.py /app/

RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN useradd --no-create-home -G dialout nginx

RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache


COPY nginx.conf /etc/nginx/
COPY flask-site-nginx.conf /etc/nginx/conf.d/
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/

# Make port 21001 available to the world outside this container
EXPOSE 21001:21001

# Define environment variable
ENV NAME tracerbn_api

# Set proxy server, replace host:port with values for your servers 
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
