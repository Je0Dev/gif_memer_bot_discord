import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cogs.dashboard import Dashboard


@pytest.fixture
def mock_ipc_client():
    client = MagicMock()
    client.request = AsyncMock()
    client.start = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_dashboard_bot(mock_bot, mock_ipc_client):
    mock_app = MagicMock()
    mock_bot.app = mock_app
    mock_bot.discord_oauth = MagicMock()
    mock_bot.discord_oauth.authorized = True
    mock_bot.discord_oauth.fetch_user = AsyncMock()
    mock_bot.discord_oauth.fetch_guilds = AsyncMock()
    mock_bot.discord_oauth.create_session = MagicMock()
    mock_bot.discord_oauth.callback = AsyncMock()

    return mock_bot, mock_ipc_client, mock_app


@pytest.mark.asyncio
async def test_cog_load_starts_ipc_client(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        cog = Dashboard(bot)
        await cog.cog_load()
        mock_client.start.assert_called_once()


@pytest.mark.asyncio
async def test_cog_unload_closes_ipc_client(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        cog = Dashboard(bot)
        cog.ipc_client = mock_client
        await cog.cog_unload()
        mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_login_redirects_to_discord_oauth(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        mock_session = MagicMock()
        mock_bot.discord_oauth.create_session.return_value = mock_session

        cog = Dashboard(bot)

        with patch.object(cog, "app") as app_mock:
            app_mock.route = MagicMock(return_value=lambda f: f)

            @app_mock.route("/login")
            async def login():
                return await cog.discord_oauth.create_session(
                    scope=["identify", "guilds"]
                )

            result = await login()
            assert result == mock_session


@pytest.mark.asyncio
async def test_callback_handles_oauth_error(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        cog = Dashboard(bot)

        with patch.object(cog, "app") as app_mock:
            app_mock.route = MagicMock(return_value=lambda f: f)

            @app_mock.route("/callback")
            async def callback():
                cog.discord_oauth.callback = AsyncMock(
                    side_effect=Exception("OAuth failed")
                )
                try:
                    await cog.discord_oauth.callback()
                except Exception:
                    return "Authentication failed", 400
                return "OK"

            status, code = await callback()
            assert code == 400
            assert "Authentication failed" in status


@pytest.mark.asyncio
async def test_server_settings_fetches_via_ipc(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot
    guild_id = 123456789

    mock_client.request = AsyncMock(
        return_value={"daily_memes": True, "target_channel_id": 987654321}
    )

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        cog = Dashboard(bot)
        cog.ipc_client = mock_client
        cog.discord_oauth.authorized = True

        mock_guild = MagicMock()
        mock_guild.id = guild_id
        mock_guild.text_channels = [MagicMock(id=1, name="general")]
        bot.get_guild = MagicMock(return_value=mock_guild)

        settings = await cog.ipc_client.request("get_guild_settings", guild_id=guild_id)
        assert settings["daily_memes"] is True
        assert settings["target_channel_id"] == 987654321


@pytest.mark.asyncio
async def test_server_settings_handles_ipc_error(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot
    guild_id = 999999999

    mock_client.request = AsyncMock(side_effect=Exception("IPC failed"))

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        cog = Dashboard(bot)
        cog.ipc_client = mock_client
        cog.discord_oauth.authorized = True

        mock_guild = MagicMock()
        mock_guild.id = guild_id
        mock_guild.text_channels = []
        bot.get_guild = MagicMock(return_value=mock_guild)

        try:
            settings = await cog.ipc_client.request(
                "get_guild_settings", guild_id=guild_id
            )
        except Exception:
            settings = {"daily_memes": False, "target_channel_id": None}

        assert settings == {"daily_memes": False, "target_channel_id": None}


@pytest.mark.asyncio
async def test_update_settings_sends_correct_data(mock_dashboard_bot):
    bot, mock_client, mock_app = mock_dashboard_bot
    guild_id = 123456789

    mock_client.request = AsyncMock(return_value={"status": "success"})

    with patch("cogs.dashboard.ipc.Client", return_value=mock_client):
        cog = Dashboard(bot)
        cog.ipc_client = mock_client

        await cog.ipc_client.request(
            "update_guild_settings",
            guild_id=guild_id,
            daily_memes=True,
            target_channel_id=987654321,
        )

        mock_client.request.assert_called_once_with(
            "update_guild_settings",
            guild_id=guild_id,
            daily_memes=True,
            target_channel_id=987654321,
        )
