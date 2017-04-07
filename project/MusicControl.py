import json
import requests
import logging

logging.basicConfig(level=logging.WARNING,format='(%(threadName)-9s) %(message)s',)
requests_log = logging.getLogger("requests")
requests_log.addHandler(logging.NullHandler())
requests_log.propagate = False

class Music():
    """A simple client to control mopidy"""

    def __init__(self, url="http://127.0.0.1/mopidy/rpc", u_id=3):
        self.url = url
        self.u_id = u_id
        self.header = {'content-type': 'application/json'}

    def server_alive(self):
        try:
            r = requests.get("http://127.0.0.1")
        except requests.ConnectionError as err:
            return False

        if r.status_code == 200:
            return True
        else:
            return False

    def load_playlist(self, uri="spotify:user:estellecaswell:playlist:5KpHR1UysAms2zssDHeSbZ"):
        payload = {"method": "core.tracklist.add", "jsonrpc": "2.0", "params": { "uri": uri }, "id": self.u_id}
        response_data = requests.post(self.url, data=json.dumps(payload), headers=self.header)
        return response_data.json()

    def play(self):
        payload = {"method": "core.playback.play", "jsonrpc": "2.0", "params": {}, "id": self.u_id}
        response_data = requests.post(self.url, data=json.dumps(payload), headers=self.header)
        return response_data.json()

    def next_track(self):
        payload = {"method": "core.playback.next", "jsonrpc": "2.0", "params": {}, "id": self.u_id}
        response_data = requests.post(self.url, data=json.dumps(payload), headers=self.header)
        return response_data.json()

    def pause(self):
        payload = {"method": "core.playback.pause", "jsonrpc": "2.0", "params": {}, "id": self.u_id}
        response_data = requests.post(self.url, data=json.dumps(payload), headers=self.header)
        return response_data.json()

    def state(self):
        payload = {"method": "core.playback.get_state", "jsonrpc": "2.0", "params": {}, "id": self.u_id}
        response_data = requests.post(self.url, data=json.dumps(payload), headers=self.header)
        return response_data.json()

    def get_track(self):
        payload = {"method": "core.playback.get_current_track", "jsonrpc": "2.0", "params": {}, "id": self.u_id}
        response_data = requests.post(self.url, data=json.dumps(payload), headers=self.header)
        return response_data.json()
