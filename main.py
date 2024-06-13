import os
import globals as gl

# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

# Import actions
from .actions.message import SendMessage
from .actions.chat_mode import ChatMode
from .actions.clip import Clip
from .actions.marker import Marker
from .actions.viewers import Viewers


class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__()

        self.lm = self.locale_manager
        self.lm.set_to_os_default()

        # Launch backend
        backend_path = os.path.join(self.PATH, "twitch_backend.py")
        self.launch_backend(backend_path=backend_path, open_in_terminal=False)
        self.wait_for_backend(tries=5)

        settings = self.get_settings()
        client_id = settings.get('client_id', '')
        client_secret = settings.get('client_secret', '')
        auth_code = settings.get('auth_code', '')

        self.backend.set_token_path(os.path.join(
            gl.DATA_PATH, 'settings', 'plugins', self.get_plugin_id_from_folder_name(), 'keys.json'))

        if client_id and client_secret and auth_code:
            self.backend.auth_with_code(
                client_id, client_secret, auth_code)

        # Register actions
        self.message_action_holder = ActionHolder(
            plugin_base=self,
            action_base=SendMessage,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::SendMessage",
            action_name="Send Chat Message",
        )
        self.add_action_holder(self.message_action_holder)

        self.viewer_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Viewers,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::Viewers",
            action_name="Show Viewers",
        )
        self.add_action_holder(self.viewer_action_holder)

        self.marker_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Marker,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::Marker",
            action_name="Create Stream Marker"
        )
        self.add_action_holder(self.marker_action_holder)

        self.chat_mode_action_holder = ActionHolder(
            plugin_base=self,
            action_base=ChatMode,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::ChatMode",
            action_name="Toggle Chat Mode"
        )
        self.add_action_holder(self.chat_mode_action_holder)

        self.clip_action_holder = ActionHolder(
            plugin_base=self,
            action_base=Clip,
            action_id="com_imdevinc_StreamControllerTwitchPlugin::Clip",
            action_name="Create Clip"
        )
        self.add_action_holder(self.clip_action_holder)

        # Register plugin
        self.register(
            plugin_name="Twitch Integration",
            github_repo="https://github.com/imdevinc/StreamControllerTwitchPlugin",
            plugin_version="1.0.0",
            app_version="1.1.1-alpha"
        )
        self.add_css_stylesheet(os.path.join(self.PATH, "style.css"))

    def save_auth_settings(self, client_id: str, client_secret: str, auth_code: str) -> None:
        settings = self.get_settings()
        settings['client_id'] = client_id
        settings['client_secret'] = client_secret
        settings['auth_code'] = auth_code
        self.set_settings(settings)
