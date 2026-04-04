import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cogs.settings import Settings

class MockData:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.mark.asyncio
async def test_get_guild_settings_existing(mock_bot):
    cog = Settings(mock_bot)
    cog.db = AsyncMock()
    
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=(1, 123456789))
    cog.db.execute.return_value.__aenter__.return_value = mock_cursor

    data = MockData(guild_id=100)
    result = await cog.get_guild_settings(data)
    
    assert result["daily_memes"] is True
    assert result["target_channel_id"] == 123456789

@pytest.mark.asyncio
async def test_get_guild_settings_new(mock_bot):
    cog = Settings(mock_bot)
    cog.db = AsyncMock()
    
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=None)
    cog.db.execute.return_value.__aenter__.return_value = mock_cursor

    data = MockData(guild_id=100)
    result = await cog.get_guild_settings(data)
    
    assert result["daily_memes"] is False
    assert result["target_channel_id"] is None

@pytest.mark.asyncio
async def test_update_guild_settings(mock_bot):
    cog = Settings(mock_bot)
    cog.db = AsyncMock()
    cog.db.execute = AsyncMock()
    cog.db.commit = AsyncMock()

    data = MockData(guild_id=100, daily_memes=True, target_channel_id=987654321)
    result = await cog.update_guild_settings(data)
    
    assert result["status"] == "success"
    assert cog.db.execute.call_count == 1
    assert cog.db.commit.call_count == 1

@pytest.mark.asyncio
async def test_get_guild_settings_invalid_id(mock_bot):
    cog = Settings(mock_bot)
    cog.db = AsyncMock()
    
    data = MockData(guild_id=0)
    result = await cog.get_guild_settings(data)
    
    assert "error" in result
