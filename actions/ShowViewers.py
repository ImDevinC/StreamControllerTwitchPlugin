from enum import StrEnum
from threading import Thread
from time import sleep
from typing import Optional, Union

from gi.repository import GLib
from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input

from loguru import logger as log

from constants import VIEWER_UPDATE_INTERVAL_SECONDS


class Icons(StrEnum):
    VIEWERS = "view"


class ShowViewers(TwitchCore):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.VIEWERS]
        self.current_icon = self.get_icon(Icons.VIEWERS)
        self.icon_name = Icons.VIEWERS

    def on_ready(self) -> None:
        Thread(target=self._update_viewers, daemon=True, name="update_viewers").start()

    def _update_viewers(self) -> None:
        while self.get_is_present():
            count: Union[Optional[int], str] = self.backend.get_viewers()
            if not count:
                count = "-"
            GLib.idle_add(lambda c=count: self.set_center_label(str(c)))
            sleep(VIEWER_UPDATE_INTERVAL_SECONDS)
