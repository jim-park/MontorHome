# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Define environment variable
ENV NAME mh_api

# Set the working directory to /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y install nginx supervisor gcc

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# All packages built, remove gcc and purge to save space.
RUN apt-get remove gcc -y
RUN apt autoremove --purge -y

# Create user for nginx.
RUN useradd --no-create-home -G dialout nginx

# Tidy up.
RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache

# Make port 21001 available to the world outside this container
EXPOSE 21001:21001

# Copy required files into place.
COPY nginx.conf /etc/nginx/
COPY flask-site-nginx.conf /etc/nginx/conf.d/
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/
COPY *.py /app/

# Set proxy server, replace host:port with values for your servers 
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
