import os
import globals as gl
import json

from loguru import logger

# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import actions
from .settings import PluginSettings
from .actions.message import SendMessage
from .actions.chat_mode import ChatMode
from .actions.clip import Clip
from .actions.marker import Marker
from .actions.viewers import Viewers
from .actions.play_ad import PlayAd
from .actions.snooze_ad import SnoozeAd
from .actions.ad_schedule import NextAd


class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__()

        self.has_plugin_settings = True

        self.lm = self.locale_manager
        self.lm.set_to_os_default()

        self._settings_manager = PluginSettings(self)

        self.auth_callback_fn: callable = None

        # Launch backend
        backend_path = os.path.join(self.PATH, "twitch_backend.py")
        self.launch_backend(backend_path=backend_path, open_in_terminal=False,
                            venv_path=os.path.join(self.PATH, ".venv"))
        self.wait_for_backend(tries=5)

        settings = self.get_settings()
        client_id = settings.get('client_id', '')
        client_secret = settings.get('client_secret', '')
        auth_code = settings.get('auth_code', '')

        settings_path = os.path.join(
            gl.DATA_PATH, 'settings', 'plugins', self.get_plugin_id_from_folder_name())
        os.makedirs(settings_path, exist_ok=True)
        self.backend.set_token_path(os.path.join(settings_path, "keys.json"))
        if client_id and client_secret and auth_code:
            self.backend.auth_with_code(
                client_id, client_secret, auth_code)

        # Register actions
        self.message_action_holder = ActionHolder(
            plugin_base=self,
            action_base=SendMessage,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::SendMessage",
            action_name="Send Chat Message",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.message_action_holder)

        self.viewer_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Viewers,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::Viewers",
            action_name="Show Viewers",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.viewer_action_holder)

        self.marker_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Marker,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::Marker",
            action_name="Create Stream Marker",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.marker_action_holder)

        self.chat_mode_action_holder = ActionHolder(
            plugin_base=self,
            action_base=ChatMode,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::ChatMode",
            action_name="Toggle Chat Mode",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.chat_mode_action_holder)

        self.clip_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Clip,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::Clip",
            action_name="Create Clip",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.clip_action_holder)

        self.snooze_ad_action_holder = ActionHolder(
            plugin_base=self,
            action_base=SnoozeAd,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::SnoozeAd",
            action_name="Snooze Ad",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.snooze_ad_action_holder)

        self.play_ad_action_holder = ActionHolder(
            plugin_base=self,
            action_base=PlayAd,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::PlayAd",
            action_name="Play Ad",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.play_ad_action_holder)

        # self.next_ad_action_holder = ActionHolder(
        #    plugin_base=self,
        #    action_base=NextAd,
        #    action_id="com_imdevinc_StreamControllerTwitchPlugin::NextAd",
        #    action_name="Next Ad",
        #    action_support={
        #        Input.Key: ActionInputSupport.SUPPORTED,
        #        Input.Dial: ActionInputSupport.UNTESTED,
        #        Input.Touchscreen: ActionInputSupport.UNTESTED,
        #    }
        # )
        # self.add_action_holder(self.next_ad_action_holder)

        try:
            with open(os.path.join(self.PATH, "manifest.json"), "r", encoding="UTF-8") as f:
                data = json.load(f)
        except Exception as ex:
            logger.error(ex)
            data = {}
        app_manifest = {
            "plugin_version": data.get("version", "0.0.0"),
            "app_version": data.get("app-version", "0.0.0")
        }

        # Register plugin
        self.register(
            plugin_name="Twitch Integration",
            github_repo="https://github.com/imdevinc/StreamControllerTwitchPlugin",
            plugin_version=app_manifest.get("plugin_version"),
            app_version=app_manifest.get("app_version")
        )
        self.add_css_stylesheet(os.path.join(self.PATH, "style.css"))

    def save_auth_settings(self, client_id: str, client_secret: str, auth_code: str) -> None:
        settings = self.get_settings()
        settings['client_id'] = client_id
        settings['client_secret'] = client_secret
        settings['auth_code'] = auth_code
        self.set_settings(settings)

    def on_auth_callback(self, success: bool, message: str = "") -> None:
        if self.auth_callback_fn:
            self.auth_callback_fn(success, message)

    def get_settings_area(self):
        return self._settings_manager.get_settings_area()
