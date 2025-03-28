from ufc import UFCSimAppProHelper

import socket
import json
import binascii
import struct 
import math
#import config
opt1 = 0	
opt2 = 0
opt3 = 0
opt4 = 0
opt5 = 0
nav1 = 0
inav1 = 0
comm1 = 0
rad_alt = 0
VHFString1 =""
start = 0
from XPPython3 import xp
#----------------------------------------------------------------------------------------
def UDf(opt1,opt2, opt3, opt4, opt5, inav1,scrpad):
  global start
  def send_json_udp_message(json_data, host='localhost', port=16536):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(json.dumps(json_data).encode('utf-8'), (host, port))
  if(start==0):   # only run once
    start = 1
    simapp_pro_start_messages = [
      {"func": "net", "msg": "ready"},
      {"func": "mission", "msg": "ready"},
      {"func": "mission", "msg": "start"},
      {"func": "mod", "msg": "FA-18C_hornet"}
    ]

    
    # Connect to SimApp Pro and prepare to start receiving data
    for payload in simapp_pro_start_messages:
      send_json_udp_message(payload)


    # Create a UFC payload
  ufc_payload = {
      "option1": str(opt1), 
      "option2": str(opt2),
      "option3": str(opt3),
      "option4": str(opt4),
      "option5": str(opt5),
      "com1": "T",
      "com2": "6",
      "scratchPadNumbers": str(scrpad),
      "scratchPadString1": "S",
      "scratchPadString2": "P",
      "selectedWindows": ["1"]
      }
  ufcHelper = UFCSimAppProHelper(ufc_payload)

  # Create the SimApp Pro messaged it needs to update the UFC
  simapp_pro_ufc_payload = {
      "args": {
          "FA-18C_hornet": ufcHelper.get_ufc_payload_string(),
      },
      "func": "addCommon",
      "timestamp": 0.00
  }

  simapp_pro_set_brightness = {
      "args": {
          "0": {
              "109": "0.95"
          }
      },
      "func": "addOutput",
      "timestamp": 0
  }

  # Send message to SimApp Pro
  send_json_udp_message(simapp_pro_ufc_payload)
# send_json_udp_message(simapp_pro_set_brightness)  




class PythonInterface:
#     def __init__(self):
#         self.thread = None
#         self.shared_data = {}
#         self.floop = None
        
    def XPluginStart(self):
        self.Name = "WinWing UDP v1.0"
        self.Sig = "simData1.demos.xppython3"
        self.Desc = "A plugin that controls WW UDP."
        self.nav1 = xp.findDataRef("sim/cockpit/radios/nav1_freq_hz")
        self.rad_alt = xp.findDataRef("sim/cockpit2/gauges/indicators/radio_altimeter_height_ft_pilot")
        self.achdg = xp.findDataRef("sim/flightmodel/position/mag_psi") 
        self.airspd = xp.findDataRef("sim/flightmodel/position/indicated_airspeed")
        self.gspd = xp.findDataRef("sim/flightmodel/position/groundspeed")
        self.hdg = xp.findDataRef("sim/cockpit/autopilot/heading_mag")
        self.scrpad = xp.findDataRef("SRS/X-KeyPad/numeric_buffer_value")
            # We use a simple flight loop in order to periodically see and display
        xp.registerFlightLoopCallback(self.FlightLoopCallback, 1.0, 0)         
        
        return self.Name, self.Sig, self.Desc                    
                              


    def XPluginStop(self):
                # Unregister the callback
        xp.unregisterFlightLoopCallback(self.FlightLoopCallback, 0)

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        if self.floop:
            xp.destroyFlightLoop(self.floop)
            self.floop = None

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass
    
    def FlightLoopCallback(self, elapsedMe, elapsedSim, counter, refcon):
    # Simple flight loop 

        opt1 = xp.getDataf(self.rad_alt)
        if (opt1 > 2500):
            opt1 = 9999
        opt1 ="{:.0f}".format(opt1)
        opt1 = str(opt1).zfill(4)
        
        opt2 = xp.getDataf(self.achdg)
        opt2 ="{:.0f}".format(opt2)
        opt2 = str(opt2).zfill(3)
        
        opt3 = xp.getDataf(self.airspd)
        opt3 ="{:.0f}".format(opt3)
        opt3 = str(opt3).zfill(3)
        
        opt4 = xp.getDataf(self.gspd)
        opt4 = opt4*1.94384
        opt4 ="{:.0f}".format(opt4)
        opt4 = str(opt4).zfill(3)          
        
        opt5 = xp.getDataf(self.hdg)
        opt5 ="{:.0f}".format(opt5)
        opt5 = str(opt5).zfill(3)        
        
        inav1 = xp.getDatai(self.nav1)
        inav1 =  "{: .0f}".format(inav1*10)
        
        scrpad = xp.getDataf(self.scrpad)
        scrpad = "{:.0f}".format(scrpad)        


        UDf(opt1,opt2, opt3, opt4, opt5, inav1, scrpad)
        return 1.0

