import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pytestmark = [pytest.mark.integration]


@pytest.fixture
def mock_quart_app():
    app = MagicMock()
    app.config = {}
    return app


@pytest.fixture
def mock_discord_oauth():
    oauth = MagicMock()
    oauth.authorized = True
    oauth.fetch_user = AsyncMock()
    oauth.fetch_guilds = AsyncMock()
    oauth.create_session = MagicMock()
    oauth.callback = AsyncMock()
    return oauth


@pytest.mark.asyncio
async def test_full_flow_meme_command(mock_bot, mock_ctx):
    from cogs.memes import Memes

    mock_bot.http_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "title": "Test Meme",
            "url": "https://example.com/meme.jpg",
            "subreddit": "memes",
            "ups": 100,
        }
    )
    mock_bot.http_session.get.return_value.__aenter__.return_value = mock_response

    cog = Memes(mock_bot)
    await cog.meme(mock_ctx)

    mock_ctx.send.assert_called_once()
    args, kwargs = mock_ctx.send.call_args
    assert "embed" in kwargs


@pytest.mark.asyncio
async def test_full_flow_gif_command_with_fallback(mock_bot, mock_ctx):
    from cogs.memes import Memes

    mock_bot.http_session = AsyncMock()

    klipy_response = AsyncMock()
    klipy_response.status = 500

    giphy_response = AsyncMock()
    giphy_response.status = 200
    giphy_response.json = AsyncMock(
        return_value={
            "data": [
                {"title": "Fallback GIF", "url": "https://example.com/fallback.gif"}
            ]
        }
    )

    mock_bot.http_session.get.side_effect = [klipy_response, giphy_response]

    with patch.dict(os.environ, {"KLIPY_API_KEY": "test", "GIPHY_API_KEY": "test"}):
        cog = Memes(mock_bot)
        await cog.gif(mock_ctx, query="test")

        mock_ctx.send.assert_called_once()
        args, kwargs = mock_ctx.send.call_args
        assert "embed" in kwargs


@pytest.mark.asyncio
async def test_settings_database_integration(mock_bot, mock_db):
    from cogs.settings import Settings

    with patch("cogs.settings.aiosqlite") as mock_aiosqlite:
        mock_aiosqlite.connect = AsyncMock(return_value=mock_db)
        cog = Settings(mock_bot)
        await cog.cog_load()

        mock_aiosqlite.connect.assert_called_once()
        mock_db.execute.assert_called()


@pytest.mark.asyncio
async def test_guild_settings_persistence(mock_bot, mock_db):
    from cogs.settings import Settings

    cog = Settings(mock_bot)
    cog.db = mock_db

    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=(1, 123456789))
    mock_db.execute.return_value.__aenter__.return_value = mock_cursor

    class MockData:
        guild_id = 100
        daily_memes = True
        target_channel_id = 123456789

    result = await cog.update_guild_settings(MockData())
    assert result["status"] == "success"

    mock_db.execute.assert_called()
    mock_db.commit.assert_called()

    result = await cog.get_guild_settings(MockData())
    assert result["daily_memes"] is True
    assert result["target_channel_id"] == 123456789
