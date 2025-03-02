import threading
import time
import os

from src.backend.PluginManager.ActionBase import ActionBase

from loguru import logger as log

# Currently an issue with TwitchPy that gets the wrong time format, can't use this yet


class NextAd(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ad_thread: threading.Thread = None
        self.has_configuration = True

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "view.png"), size=0.85)
        if not self.__ad_thread or not self.__ad_thread.is_alive():
            self.__ad_thread = threading.Thread(
                target=self.ad_thread, daemon=True, name="ad_thread")
            self.__ad_thread.start()

    def ad_thread(self):
        while True:
            if not self.get_is_present():
                return
            self.get_next_ad()
            time.sleep(1)

    def get_next_ad(self):
        try:
            next_ad = self.plugin_base.backend.get_next_ad()
            if not next_ad:
                next_ad = "-"
            self.set_bottom_label(str(next_ad))
            self.hide_error()
        except Exception as ex:
            log.error(ex)
            self.show_error()
