#!/usr/bin/env python

"""
Python module to fetch departure times from Translink's Real-Time
Transit Information API.

Includes:

get_next_buses(stop_number=default_stop_number, time_format="%-I:%Mpm")
- returns a dictionary containing the times for the next two buses
departing from the specified stop.

default_stop_number - set this to your favourite stop number to save
typing one in every time.

params - dictionary containing various API parameters including the
API key to be used.

To use this module you need to register and acquire an API key
from Translink from the website link below.

Translink API Reference:
https://developer.translink.ca/ServicesRtti/ApiReference
"""

import requests
import sys
from xml.etree import ElementTree

api_key = "{Insert your API key from Translink here}"
stops_url = "http://api.translink.ca/RTTIAPI/V1/stops/{}"
stop_estimates_url = "http://api.translink.ca/RTTIAPI/V1/stops/{}/estimates"

# Default stop number
default_stop_number = 51034 # Arbutus St at W 15 Ave


params = {
    'apiKey': api_key,
    'Count': 2, # The number of buses to return. Default 6
    'TimeFrame': 40  # The search time frame in minutes. Default 1440
    #'RouteNo': # If present, will search for stops specific to route
}

headers = {'content-type': 'application/json'}  # This doesn't work for some reason
# Get XML instead.

def get_next_buses(stop_number=default_stop_number):

    r = requests.get(stop_estimates_url.format(stop_number), params=params, headers=headers)

    r.raise_for_status()

    root = ElementTree.fromstring(r.content)

    code = None
    buses = []

    for child in root:
        if child.tag == 'Code':
            code = child.text
        if child.tag == 'Message':
            message = child.text
        if child.tag == 'NextBus':
            buses.append(child)

    if code:
        print("Error code {}: {}".format(code, message))
        return None

    leave_times = {}

    for bus in buses:
        route = bus.find('RouteNo').text
        schedule = bus.find('Schedules')
        schedules = schedule.findall('Schedule')
        times = []
        for s in schedules:
            times.append(s.find('ExpectedLeaveTime').text)
        leave_times[route] = times
    return leave_times



if __name__ == "__main__":
    print(get_next_buses(*sys.argv[1:]))
