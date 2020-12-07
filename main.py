import json
import os
from datetime import datetime

import urllib3  # noqa
from requests import get

from constants import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FILENAME = "uptime.json"

if not os.path.exists(FILENAME):
    with open(FILENAME, "w") as file:
        file.write("{}")


@schedule(DELAY)
def uptime_func():
    t = datetime.now(TZ).time()
    if not (START_TIME <= t <= END_TIME):
        return
    res = get(SERVER, verify=False)
    data = json.load(open(FILENAME))
    old_uptime = data.get(SERVER, False)
    uptime = res.status_code == 200
    if uptime != old_uptime:
        msg = (MESSAGE_UP if uptime else MESSAGE_DOWN).format(server=SERVER)
        send_message(msg, peer_id=VK_PEER_ID)
    data[SERVER] = uptime
    json.dump(data, open(FILENAME, "w"))


if __name__ == '__main__':
    uptime_func()
    print("Start")
    run()
