from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope
from twitchAPI.oauth import UserAuthenticator
from streamcontroller_plugin_tools import BackendBase

SCOPES = [AuthScope.USER_WRITE_CHAT, AuthScope.CHANNEL_MANAGE_BROADCAST,
          AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS, AuthScope.CLIPS_EDIT]


class Backend(BackendBase):
    def __init__(self):
        super().__init__()
        self.twitch: Twitch = Twitch('', authenticate_app=False)
        self.auth: UserAuthenticator = None
        self.user_id: str = None
        self.client_id: str = None
        self.client_secret: str = None
        self.access_token: str = None
        self.refresh_token: str = None

    async def create_clip(self) -> None:
        await self.twitch.create_clip(self.user_id)

    async def create_marker(self) -> None:
        await self.twitch.create_stream_marker(self.user_id)

    async def get_viewers(self) -> int:
        await self.twitch.get_streams(first=1, user_id=self.user_id, stream_type='live')

    async def toggle_chat_mode(self, mode: str) -> None:
        current = await self.twitch.get_chat_settings(self.user_id)
        updated = not current[mode]
        await self.update_chat_settings(self.user_id, self.user_id, **{mode: updated})

    async def send_message(self, message: str) -> None:
        await self.twitch.send_chat_message(self.user_id, self.user_id, message)

    async def update_client_credentials(self, client_id: str, client_secret: str) -> None:
        self.twitch = await Twitch(client_id, client_secret)
        self.auth = UserAuthenticator(
            self.twitch, SCOPES, url='http://localhost:3000/auth')


backend = Backend()
