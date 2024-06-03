import threading
import time
import os

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase


class Viewers(TwitchActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_count = 0

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "view.png"), size=0.85)
        threading.Thread(target=self.show_current_viewers,
                         daemon=True, name="show_current_viewers").start()

    def show_current_viewers(self):
        while True:
            self.current_count = self.plugin_base.backend.get_viewers()
            if not self.current_count:
                self.current_count = "-"
            self.set_bottom_label(str(self.current_count))
            time.sleep(30)
