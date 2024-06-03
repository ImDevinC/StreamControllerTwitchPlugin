import os

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase


class Marker(TwitchActionBase):
    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "bookmark.png"), size=0.85)

    def on_key_down(self):
        self.plugin_base.backend.create_marker()
