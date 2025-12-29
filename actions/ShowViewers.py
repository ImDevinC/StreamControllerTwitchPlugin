from enum import StrEnum
from threading import Thread
from time import sleep

from gi.repository import GLib
from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input

from loguru import logger as log


class Icons(StrEnum):
    VIEWERS = "view"


class ShowViewers(TwitchCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.VIEWERS]
        self.current_icon = self.get_icon(Icons.VIEWERS)
        self.icon_name = Icons.VIEWERS

    def on_ready(self):
        Thread(target=self._update_viewers, daemon=True,
               name="update_viewers").start()

    def _update_viewers(self):
        while self.get_is_present():
            count = self.backend.get_viewers()
            if not count:
                count = "-"
            GLib.idle_add(lambda c=count: self.set_center_label(str(c)))
            sleep(10)
