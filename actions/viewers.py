import threading
import time
import os

from loguru import logger as log

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase


class Viewers(TwitchActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_count = 0
        self._view_hidden = False

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "view.png"), size=0.85)
        threading.Thread(target=self.show_current_viewers,
                         daemon=True, name="viewers_thread").start()

    def on_key_down(self):
        self._view_hidden = not self._view_hidden
        image = "view-hidden.png" if self._view_hidden else "view.png"
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", image), size=0.85)
        self.show_current_viewers()

    def viewers_thread(self):
        while True:
            self.show_current_viewers()
            time.sleep(30)

    def show_current_viewers(self):
        if self._view_hidden:
            self.set_bottom_label("-")
            return
        try:
            self.current_count = self.plugin_base.backend.get_viewers()
            if not self.current_count:
                self.current_count = "-"
            self.set_bottom_label(str(self.current_count))
        except Exception as ex:
            log.error(ex)
            self.show_error(30)
