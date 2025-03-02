
import os

from loguru import logger as log

from src.backend.PluginManager.ActionBase import ActionBase


class Clip(ActionBase):
    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "camera.png"), size=0.85)

    def on_key_down(self):
        try:
            self.plugin_base.backend.create_clip()
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
