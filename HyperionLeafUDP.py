#!/usr/bin/env python3

from nanoleaf import Aurora #https://github.com/bharat/nanoleaf
from nanoleaf import setup

import socket
import datetime
from time import sleep
from random import *

IPstring = "192.168.0.53"  # IP address of the nanoleaf
tokenString = "LV72493cqfXlL3J0dt5dpgqUwQ2XYf9s"
# PanelIDs = (216, 35, 214, 157, 5, 112, 124)
# UDP_IP = "192.168.1.10"  # use this when testing on remote work station
# UDP_IP = "127.0.0.1" #use this when running on RPI
UDP_IP = "192.168.0.251"
UDP_PORT = 20450  # any available port, must match hyperion configuration


def GetToken():
    token = setup.generate_auth_token(IPstring)
    print(token)

def TestPanel(panel_id):
    MyPanelID = panel_id
    MyPanels = Aurora(IPstring, tokenString)
    Mystrm = MyPanels.effect_stream()
    Mystrm.panel_set(MyPanelID, 0, 0, 0)

def GetPanels():
    MyPanels = Aurora(IPstring, tokenString)
    MyPanelIDs = [x['panelId'] for x in MyPanels.panel_positions]  # retreive nanoleaf panel ID's for information only
    # print(MyPanelIDs)
    return(MyPanelIDs)

def HyperLeaf(my_panels):
    PanelIDs = my_panels[1:-1]
    lower_panel = my_panels[0]
    upper_panel = my_panels[len(my_panels)-1]
    first_panel = PanelIDs[0]
    last_panel = PanelIDs[len(PanelIDs)-1]
    print(my_panels)
    print(lower_panel)
    print(first_panel)
    print(upper_panel)
    print(last_panel)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))
    my_aurora = Aurora(IPstring, tokenString) # IP address and key for nanoleaf Aurora
    my_aurora.on = True #Turn nanoleaf on
    my_aurora.brightness = 50 #set brightness
    sleep(1)
    strm = my_aurora.effect_stream() #set nanoleaf to streaming mode, this only works with bharat's fork of nanoleaf
    # print(strm.addr)
    while True:
        data = sock.recvfrom(21)  # hyperion sends 3 bytes (R,G,B) for each configured light (3*7=21)
        now = datetime.datetime.now()  # retrieve time for debuging
        new = bytearray(data[0])  # retrieve hyperion byte array
        RGBList = list(new)  # great R-G-B list
        # print(RGBList)  # for debuging only
        PanelCount = 0  # initial condition
        for Panel in PanelIDs:  # itterate through the configured PanleID's above
            firstByteIndex = PanelCount * 3  # Red Index
            secondByteIndex = firstByteIndex + 1  # Green Index
            thirdByteIndex = secondByteIndex + 1  # Blue Index
            intPanelID = PanelIDs[PanelCount]  # This Panel ID ***could this not just be "Panel"
            intRedValue = RGBList[firstByteIndex]
            intGreenValue = RGBList[secondByteIndex]
            intBlueValue = RGBList[thirdByteIndex]
            # print(str(intPanelID) + " " + str(intRedValue) + " " + str(intGreenValue) + " " + str(intBlueValue))

            if intPanelID == lower_panel or intPanelID == first_panel:  # condition to handle two panels on the same vertical axis, or configure hyperion to drive this as well
                strm.panel_set(lower_panel, intRedValue, intGreenValue, intBlueValue)
                strm.panel_set(first_panel, intRedValue, intGreenValue, intBlueValue)
            else:
                if intPanelID == upper_panel or intPanelID == last_panel:  # condition to handle two panels on the same vertical axis, or configure hyperion to drive this as well
                    strm.panel_set(upper_panel, intRedValue, intGreenValue, intBlueValue)
                    strm.panel_set(last_panel, intRedValue, intGreenValue, intBlueValue)
                else:
                    strm.panel_set(intPanelID, intRedValue, intGreenValue, intBlueValue)  # set the current panel color
            PanelCount += 1  # next panel


# GetToken()
# print(GetPanels())
# TestPanel(93)
# TestPanel(83)
HyperLeaf(GetPanels())
