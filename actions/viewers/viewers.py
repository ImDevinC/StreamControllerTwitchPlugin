from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase
import threading
import time


class Viewers(TwitchActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_count = 0

    def on_ready(self):
        threading.Thread(target=self.show_current_viewers,
                         daemon=True, name="show_current_viewers").start()

    def show_current_viewers(self):
        self.current_count = self.plugin_base.backend.get_viewers()
        self.set_center_label(str(self.current_count))
        time.sleep(30)
        threading.Thread(target=self.show_current_viewers,
                         daemon=True, name="show_current_viewers").start()
