import pytest
from unittest.mock import AsyncMock, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.user = MagicMock()
    bot.user.id = 123456789
    bot.user.name = "TestBot"
    bot.guilds = []
    bot.http = MagicMock()
    bot.http_session = MagicMock()
    bot.http_session.get = MagicMock()
    return bot


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.id = 987654321
    return ctx


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.close = AsyncMock()
    return db


@pytest.fixture
def mock_ipc_client():
    client = MagicMock()
    client.request = AsyncMock()
    client.start = AsyncMock()
    client.close = AsyncMock()
    return client
