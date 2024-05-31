import os

# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

# Import actions
from .actions.message.message import SendMessage
from .actions.viewers.viewers import Viewers
from .actions.marker.marker import Marker
from .actions.chat_mode.chat_mode import ChatMode
from .actions.clip.clip import Clip


class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__()

        # Launch backend
        backend_path = os.path.join(self.PATH, "backend", "backend.py")
        self.launch_backend(backend_path=backend_path, open_in_terminal=True)

        self.lm = self.locale_manager
        self.lm.set_to_os_default()

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

        settings = self.get_settings()
        access_token = settings['access_token'] if 'access_token' in settings else ''
        refresh_token = settings['refresh_token'] if 'refresh_token' in settings else ''
        self.wait_for_backend()

        if access_token and refresh_token:
            self.backend.set_tokens(
                access_token, refresh_token)
        client_id = settings['client_id'] if 'client_id' in settings else ''
        client_secret = settings['client_secret'] if 'client_secret' in settings else ''
        if client_id and client_secret:
            self.backend.set_client_creds(client_id, client_secret)
