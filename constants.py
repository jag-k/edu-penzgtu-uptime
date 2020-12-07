import datetime
import random
import re
import sched
import time
from os import getenv
from typing import Callable

from dotenv import load_dotenv
from pytz import timezone
from vk_api import VkApi

load_dotenv('.env')

_RE_TIME = re.compile(r'((?P<hour>\d+?)h(?:r)?)?((?P<minute>\d+?)m)?((?P<second>\d+?)s)?')
_RE_TIMEDELTA = re.compile(r'((?P<hours>\d+?)h(?:r)?)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def _get_timedelta(time_str: str) -> datetime.timedelta:
    parts = _RE_TIMEDELTA.match(time_str)
    if not parts:
        return datetime.timedelta()
    time_params = {}
    parts = parts.groupdict()
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return datetime.timedelta(**time_params)


def _get_time(time_str: str) -> datetime.time:
    parts = _RE_TIME.match(time_str)
    time_params = {"tzinfo": TZ}
    if not parts:
        return datetime.time(**time_params)
    parts = parts.groupdict()
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return datetime.time(**time_params)


TZ = timezone(getenv("TIMEZONE"))
START_TIME = _get_time(getenv("START_TIME"))
END_TIME = _get_time(getenv("END_TIME"))
DELAY = _get_timedelta(getenv("DELAY"))

# VK
VK_LOGIN = getenv("VK_LOGIN")
VK_PASSWORD = getenv("VK_PASSWORD")
VK_PEER_ID = int(getenv("VK_PEER_ID", "0"))

session = VkApi(
    VK_LOGIN, VK_PASSWORD,
    app_id=2685278,  # Kate Mobile App
    client_secret="hHbJug59sKJie78wjrH8"
)
session.auth()

vk = session.get_api()

# MESSAGES
MESSAGE_UP = getenv("MESSAGE_UP")
MESSAGE_DOWN = getenv("MESSAGE_DOWN")

# UPTIME SERVER
SERVER = getenv("SERVER")

_scheduler = sched.scheduler(time.time, time.sleep)
run = _scheduler.run


def schedule(delay: int or datetime.timedelta, priority=1):
    if isinstance(delay, datetime.timedelta):
        delay = delay.seconds

    def wrapper(func: Callable):
        def decorate(*args, **kwargs):
            func(*args, **kwargs)
            _scheduler.enter(delay, priority, decorate, args, kwargs)

        return decorate

    return wrapper


# VK UTIL

def send_message(*message: str, peer_id: int = 0, sep=" ", **kwargs):
    return vk.messages.send(
        random_id=random.randint(1, 2147483647),
        peer_id=peer_id,
        message=sep.join(map(str, message)),
        **kwargs
    )


__all__ = (
    "TZ",
    "START_TIME",
    "END_TIME",
    "DELAY",
    "VK_LOGIN",
    "VK_PASSWORD",
    "VK_PEER_ID",
    "MESSAGE_UP",
    "MESSAGE_DOWN",
    "SERVER",
    "run",
    "schedule",
    "send_message",
)
