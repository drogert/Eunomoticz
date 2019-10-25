"""
<plugin key="EunoWallet" name="Eunomoticz" author="Drogert" version="0.0.1">
    <params>
        <param field="Address" label="IP Address" width="250px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="50px" required="true" default="21333"/>
        <param field="Username" label="RPC Username" width="250px" required="true" default="username"/>
        <param field="Password" label="RPC Password" width="250px" required="true" default="password"/>
        <param field="Mode1" label="Wallet Password" width="250px" required="false" default="password"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json
import urllib
import urllib.request
import urllib.parse
import requests
import os


class BasePlugin:
    UNITS = {
        'Balance': 1,
        'BlockHeight': 2,
        'Masternode': 3,
        'MasternodeCount': 4,
    }

    power_on = False
    masternodecount = None
    balance = None
    blockheight = None

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Debug("onStart called")

        if ("Eunomoticz" not in Images):
            Domoticz.Image('Eunomoticz.zip').Create()

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        if self.UNITS['Balance'] not in Devices:
            Domoticz.Device(Name="Balance", Unit=self.UNITS['Balance'], TypeName="Custom",
                            Options={"Custom": "Balance"}, Image=Images["Eunomoticz"].ID, Used=1).Create()
        if self.UNITS['BlockHeight'] not in Devices:
            Domoticz.Device(Name="Block Height", Unit=self.UNITS['BlockHeight'], TypeName="Custom",
                            Options={"Custom": "Block height"}, Image=Images["Eunomoticz"].ID, Used=1).Create()
        if self.UNITS['Masternode'] not in Devices:
            Domoticz.Device(Name="Masternode", Unit=self.UNITS['Masternode'], TypeName="Switch",
                            Image=Images["Eunomoticz"].ID, Used=1).Create()
        if self.UNITS['MasternodeCount'] not in Devices:
            Domoticz.Device(Name="Masternode Count", Unit=self.UNITS['MasternodeCount'], TypeName="Custom",
                            Options={"Custom": "Masternode count"}, Image=Images["Eunomoticz"].ID, Used=1).Create()

        DumpConfigToLog()
        Domoticz.Heartbeat(30)

    def onStop(self):
        Domoticz.Log("onStop called")
        return

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConect called")
        return

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        return

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called")

        if Unit == self.UNITS['Masternode']:
            if Command == 'Off':
                Domoticz.Debug("Switching all Masternodes OFF")
                StopMasternode()
                self.power_on = False
                self.SyncMasternodeButton(1)

            elif Command == 'On':
                Domoticz.Debug("Switching all Masternodes ON")
                StartMasternode()
                self.power_on = True
                self.SyncMasternodeButton(1)

    def onHeartbeat(self):
        self.SyncDevices(1)
        return

    def SyncDevices(self, TimedOut):

        self.balance, self.blockheight = GetInfo()
        self.masternodecount = GetMasternodeCount()
        UpdateDevice(self.UNITS['Balance'], 0, self.balance, TimedOut)
        UpdateDevice(self.UNITS['BlockHeight'], 0, self.blockheight, TimedOut)
        UpdateDevice(self.UNITS['MasternodeCount'], 0, self.masternodecount, TimedOut)
        return

    def SyncMasternodeButton(self, TimedOut):
        if (self.power_on == False):
            UpdateDevice(self.UNITS['Masternode'], 0, "Off", TimedOut)
        elif (self.power_on == True):
            UpdateDevice(self.UNITS['Masternode'], 1, "On", TimedOut)


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions

def GetMasternodeCount():
    try:
        url = "http://{}:{}@{}:{}/".format(Parameters["Username"], Parameters["Password"], Parameters["Address"],
                                           Parameters["Port"])
        headers = {'content-type': 'text/plain;'}
        response = requests.post(url, headers=headers, json={"method": "masternode", "params": ["count"]})
        data = json.loads(response.text)
        if data["result"] == None:
            Domoticz.Error("Cannot get masternode count. Reason: {}, code: {}".format(data["error"]["message"],
                                                                                   data["error"]["code"]))
            return
    except:
        Domoticz.Error("Failed to update Masternode Count")
        return
    masternodecount = data["result"]
    Domoticz.Log("Updating Masternode Count. New Masternode Count = {}".format(masternodecount))
    return masternodecount


def GetInfo():
    try:
        url = "http://{}:{}@{}:{}/".format(Parameters["Username"], Parameters["Password"], Parameters["Address"],
                                           Parameters["Port"])
        headers = {'content-type': 'text/plain;'}
        response = requests.post(url, headers=headers, json={"method": "getinfo", "params": []})
        data = json.loads(response.text)
        if data["result"] == None:
            Domoticz.Error("Cannot call wallet. Reason: {}, code: {}".format(data["error"]["message"],
                                                                                   data["error"]["code"]))
            return
    except:
        Domoticz.Error("Failed to update balance and blockheight")
        return

    balance = str(float(data["result"]["balance"]))
    Domoticz.Log("Updating balance. New balance = {}".format(balance))
    blockheight = str(int(data["result"]["blocks"]))
    Domoticz.Log("Updating blockheight. New blockheight = {}".format(blockheight))
    return balance, blockheight


def StopMasternode():
    try:
        url = "http://{}:{}@{}:{}/".format(Parameters["Username"], Parameters["Password"], Parameters["Address"],
                                           Parameters["Port"])
        headers = {'content-type': 'text/plain;'}
        response = requests.post(url, headers=headers,
                                 json={"method": "masternode", "params": ["stop-many", Parameters["Mode1"]]})
        data = json.loads(response.text)
        if data["result"] == None:
            Domoticz.Error("Cannot stop masternodes. Reason: {}, code: {}".format(data["error"]["message"],
                                                                                   data["error"]["code"]))
            return
    except:
        Domoticz.Error("Failed to update parameters")
        return
    stop = str(data["result"]["overall"])
    Domoticz.Log(stop)
    return


def StartMasternode():
     try:
        url = "http://{}:{}@{}:{}/".format(Parameters["Username"], Parameters["Password"], Parameters["Address"],
                                           Parameters["Port"])
        headers = {'content-type': 'text/plain;'}
        response = requests.post(url, headers=headers,
                                 json={"method": "masternode", "params": ["start-many", Parameters["Mode1"]]})
        data = json.loads(response.text)
        if data["result"] == None:
            Domoticz.Error("Cannot start masternodes. Reason: {}, code: {}".format(data["error"]["message"],
                                                                                   data["error"]["code"]))
            return
    except:
        Domoticz.Error("Failed to update parameters")
        return
    start = str(data["result"]["overall"])
    Domoticz.Log(start)
    return


def check_ping():
    hostname = Parameters["Address"]
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        return True
    else:
        return False
        # Domoticz.Error("Failed to connect to wallet, check if its online")


def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (Devices[Unit].TimedOut != TimedOut):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")
    return


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
