
import os

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase


class Clip(TwitchActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "camera.png"), size=0.85)

    def on_key_down(self):
        try:
            self.plugin_base.backend.create_clip()
        except:
            self.show_error()
