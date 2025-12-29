import os
import globals as gl
import json
from typing import Optional, Callable, Any

from loguru import logger
from gi.repository import Gtk

# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.DeckManagement.ImageHelpers import image2pixbuf

# Import actions
from .settings import PluginSettings
from .actions.SendMessage import SendMessage
from .actions.Clip import Clip
from .actions.ShowViewers import ShowViewers
from .actions.Marker import Marker
from .actions.ChatMode import ChatMode
from .actions.PlayAd import PlayAd
from .actions.AdSchedule import AdSchedule


class PluginTemplate(PluginBase):
    """Twitch StreamController Plugin.

    Provides integration with Twitch for StreamController, enabling actions like:
    - Creating clips and stream markers
    - Sending chat messages
    - Displaying viewer counts
    - Managing chat modes (follower-only, emote-only, slow mode, etc.)
    - Playing ads and managing ad schedules

    All Twitch API calls are rate-limited to prevent exceeding API limits.
    """

    def get_selector_icon(self) -> Gtk.Widget:
        _, rendered = self.asset_manager.icons.get_asset_values("main")
        return Gtk.Image.new_from_pixbuf(image2pixbuf(rendered))

    def _add_icons(self) -> None:
        self.add_icon("main", self.get_asset_path("glitch_flat_purple.png"))
        self.add_icon("chat", self.get_asset_path("chat.png"))
        self.add_icon("camera", self.get_asset_path("camera.png"))
        self.add_icon("bookmark", self.get_asset_path("bookmark.png"))
        self.add_icon("view", self.get_asset_path("view.png"))
        self.add_icon("follower_mode", self.get_asset_path("follower.png"))
        self.add_icon("subscriber_mode", self.get_asset_path("subscriber.png"))
        self.add_icon("emote_mode", self.get_asset_path("emote.png"))
        self.add_icon("slow_mode", self.get_asset_path("slow.png"))
        self.add_icon("money", self.get_asset_path("money.png"))
        self.add_icon("delay", self.get_asset_path("delay.png"))

    def _add_colors(self) -> None:
        self.add_color("default", [0, 0, 0, 0])
        self.add_color("warning", [255, 244, 79, 255])
        self.add_color("alert", [224, 102, 102, 255])

    def _register_actions(self) -> None:
        self.message_action_holder = ActionHolder(
            plugin_base=self,
            action_base=SendMessage,
            action_id_suffix="SendMessage",
            action_name="Send Chat Message",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.message_action_holder)

        self.clip_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Clip,
            action_id_suffix="Clip",
            action_name="Create clip",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.clip_action_holder)

        self.viewers_action_holder = ActionHolder(
            plugin_base=self,
            action_base=ShowViewers,
            action_id_suffix="ShowViewers",
            action_name="Show Viewers",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.viewers_action_holder)

        self.marker_actions_holder = ActionHolder(
            plugin_base=self,
            action_base=Marker,
            action_id_suffix="Marker",
            action_name="Create Marker",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.marker_actions_holder)

        self.chatmode_actions_holder = ActionHolder(
            plugin_base=self,
            action_base=ChatMode,
            action_id_suffix="ChatMode",
            action_name="Chat Mode",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.chatmode_actions_holder)

        self.playad_action_holder = ActionHolder(
            plugin_base=self,
            action_base=PlayAd,
            action_id_suffix="PlayAd",
            action_name="Play Ad",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.playad_action_holder)

        self.ad_schedule_action_holder = ActionHolder(
            plugin_base=self,
            action_base=AdSchedule,
            action_id_suffix="AdSchedule",
            action_name="Ad Schedule",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.ad_schedule_action_holder)

    def _setup_backend(self) -> bool:
        backend_path = os.path.join(self.PATH, "twitch_backend.py")
        self.launch_backend(
            backend_path=backend_path,
            open_in_terminal=False,
            venv_path=os.path.join(self.PATH, ".venv"),
        )
        backend_ready = self.wait_for_backend(tries=5)
        if not backend_ready:
            logger.error("Failed to initialize Twitch backend after 5 attempts")

        settings = self.get_settings()
        client_id = settings.get("client_id", "")
        client_secret = settings.get("client_secret", "")
        auth_code = settings.get("auth_code", "")

        settings_path = os.path.join(
            gl.DATA_PATH, "settings", "plugins", self.get_plugin_id_from_folder_name()
        )
        os.makedirs(settings_path, exist_ok=True)
        self.backend.set_token_path(os.path.join(settings_path, "keys.json"))
        if client_id and client_secret and auth_code:
            self.backend.auth_with_code(client_id, client_secret, auth_code)
        return True

    def __init__(self) -> None:
        super().__init__(use_legacy_locale=False)

        self.has_plugin_settings = True
        self.lm = self.locale_manager
        self.lm.set_to_os_default()
        self._settings_manager: PluginSettings = PluginSettings(self)
        self.auth_callback_fn: Optional[Callable[[bool, str], None]] = None
        self.backend_initialized: bool = False

        self._add_icons()
        self._add_colors()
        self.backend_initialized = self._setup_backend()
        if not self.backend_initialized:
            logger.warning(
                "Twitch plugin loaded but backend failed to initialize. Please check settings."
            )
        self._register_actions()

        try:
            with open(
                os.path.join(self.PATH, "manifest.json"), "r", encoding="UTF-8"
            ) as f:
                data = json.load(f)
        except Exception as ex:
            logger.error(ex)
            data = {}
        app_manifest = {
            "plugin_version": data.get("version", "0.0.0"),
            "app_version": data.get("app-version", "0.0.0"),
        }

        self.register(
            plugin_name="Twitch Integration",
            github_repo="https://github.com/imdevinc/StreamControllerTwitchPlugin",
            plugin_version=app_manifest.get("plugin_version"),
            app_version=app_manifest.get("app_version"),
        )
        self.add_css_stylesheet(os.path.join(self.PATH, "style.css"))

    def save_auth_settings(
        self, client_id: str, client_secret: str, auth_code: str
    ) -> None:
        settings = self.get_settings()
        settings["client_id"] = client_id
        settings["client_secret"] = client_secret
        settings["auth_code"] = auth_code
        self.set_settings(settings)

    def on_auth_callback(self, success: bool, message: str = "") -> None:
        if self.auth_callback_fn:
            self.auth_callback_fn(success, message)

    def get_settings_area(self) -> Any:
        return self._settings_manager.get_settings_area()
