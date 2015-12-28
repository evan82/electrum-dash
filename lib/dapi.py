from websocket import create_connection
import json

import websocket
import threading
from time import sleep

dapi = None

def on_message(ws, message):
    global dapi

    dapi.on_message(message)

def on_close(ws):
    print "### closed ###"

class DAPIWebSocket(object):    
    def start(self):
        websocket.enableTrace(True)
        self._ws = websocket.WebSocketApp("ws://localhost:5000/", on_message = on_message, on_close = on_close)
        self._wst = threading.Thread(target=self._ws.run_forever)
        self._wst.daemon = True
        self._wst.start()
        self._messages = []
        self._main_window = None

    def set_main_window(self, window):
        self._main_window = window

    def on_message(self, message):
        print "on_message", message
        obj = json.loads(message)
        if(obj["object"] == "dapi_message"):
            dapi.process_message(obj)

        self._messages.append(message)

    def send(self, json):
        self._ws.send(json)

    def receive(self):
        if len(self._messages) > 0: return self._messages.pop()
        return False

    def close(self):
        self._ws.close()

    def process_message(self, message):
        # { 
        #     "object" : "dapi_command",
        #     "data" : {
        #         "command" = "send_message",
        #         "subcommand" = "(addr,cmd2,cmd3)",
        #         "my_uid" = UID,
        #         "target_uid" = UID, 
        #         "signature" = "",
        #         "payload" = ENCRYPTED
        #     }
        # }
       

        # if(message["object"] != "dapi_message"):
        #     return False

        # if(message["data"]["command"] != "send_message"):
        #     return False

        # if(message["data"]["subcommand"] == "addr"):
        #     pass
            

        return True
    

    def get_profile(self, myusername, target_username):        
        ex = {   
            "object" : "dapi_command",
            "data" : {
                "command" : "get_profile",
                "my_uid" : myusername,
                "target_uid" : target_username, 
                "signature" : "SIG",
                "slot" : 1
            }
        }

        # send a message to DAPI
        s = json.dumps(ex)
        self.send(s)

        # wait for the result
        count = 0
        result = False
        while True:
            result = self.receive()
            if result:
                if(result.find('"dapi_result"') > 0):
                    obj = json.loads(result)
                    return obj["data"]["data"]
            
            sleep(.1)
            count += 1

            if count > 30:
                print "dapi.get_profile timeout"
                return None

        print "dapi.get_profile error"
        return None

    def send_private_message(self, myusername, target_username, subcommand, payload):
        ex = {   
            "object" : "dapi_command",
            "data" : {
                "command" : "send_message",
                "subcommand" : subcommand,
                "my_uid" : myusername,
                "target_uid" : target_username,
                "signature" : "SIG",
                "payload" : payload
            }
        }

        s = json.dumps(ex)
        print "Send:", s
        self.send(s)

        count = 0
        result = False
        while True:
            result = self.receive()
            if result:
                print "Recieve:", result
                if(result.find('"dapi_message"') > 0):
                    return result

            sleep(.1)
            count += 1

            if count > 30:
                print "dapi.get_profile timeout"
                return None

        print "dapi.get_profile error"
        return None


dapi = DAPIWebSocket()

try:
    dapi.start()
except:
    raise
    #print "DAPI is not running"

