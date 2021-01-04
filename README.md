# MontorHome

This project aims to provide real time data monitoring for remotely installed instrumentation. The data can be accessed via an an Android app or a local status web page.

This project is best described with an overall system schematic.
![MontorHome system schematic](https://docs.google.com/drawings/d/e/2PACX-1vTE8mDiYIVS3sTuNVBM3YH6iovJMq5rNCjlLHx6z9H6EGsLSPnLEZmZ-o7lq-v13J7i_yCaTvnIU1jW/pub?w=1133&h=521)

# System components
The system requires several distinct hardware components which, in-turn, require several distinct software components.

The following provides a high level description of each software component within each hardware component.

## AWS - provides an API proxy, provides a webpage to display data.
- Data to and from the remtote installation is proxied using nginx.
- Data is requested from and displayed by webpage as a dashboard.
> The code for the webpage and API can found in the folders `app_srv/mhweb/` and `app_srv/api/` respectivly.

## Android device - provides an application to fetch and display data.
- An application makes requests to the static API and displays the results.
> The Java code for the application can be found under the `android/MH/` directory

## Raspberry Pi - provides an API to acquire and return instrumentation data.
- Data is acquired and returned upon request by the Python Flask API.
> The Python code for the API and instrumentation drivers can be found under the `rasp/` directory.

## MCU - MSP430g2231 - provides a means to acquire battery 2 voltage.
- A single process samples and returns a voltage value when requested via the UART.
> The c code for the process can be found under the `msp430/` directory.
