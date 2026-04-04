import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cogs.memes import Memes

@pytest.mark.asyncio
async def test_meme_command_success(mock_bot, mock_ctx):
    cog = Memes(mock_bot)
    cog.session = AsyncMock()
    
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={
        "title": "Funny Meme",
        "url": "https://example.com/meme.jpg",
        "subreddit": "memes",
        "ups": 1500
    })
    cog.session.get.return_value.__aenter__.return_value = mock_resp

    await cog.meme(mock_ctx)
    mock_ctx.send.assert_called_once()
    args, kwargs = mock_ctx.send.call_args
    assert "embed" in kwargs

@pytest.mark.asyncio
async def test_meme_command_failure(mock_bot, mock_ctx):
    cog = Memes(mock_bot)
    cog.session = AsyncMock()
    
    mock_resp = AsyncMock()
    mock_resp.status = 500
    cog.session.get.return_value.__aenter__.return_value = mock_resp

    await cog.meme(mock_ctx)
    mock_ctx.send.assert_called_once()
    assert "Failed to fetch a meme" in str(mock_ctx.send.call_args)

@pytest.mark.asyncio
async def test_gif_command_no_keys(mock_bot, mock_ctx):
    with patch.dict(os.environ, {"KLIPY_API_KEY": "", "GIPHY_API_KEY": ""}, clear=True):
        cog = Memes(mock_bot)
        cog.session = AsyncMock()
        await cog.gif(mock_ctx)
        mock_ctx.send.assert_called_once()
        assert "No GIF API keys configured" in str(mock_ctx.send.call_args)

@pytest.mark.asyncio
async def test_gif_command_klipy_success(mock_bot, mock_ctx):
    with patch.dict(os.environ, {"KLIPY_API_KEY": "test_klipy", "GIPHY_API_KEY": ""}, clear=True):
        cog = Memes(mock_bot)
        cog.session = AsyncMock()
        
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={
            "data": [{"title": "Test GIF", "url": "https://example.com/test.gif"}]
        })
        cog.session.get.return_value.__aenter__.return_value = mock_resp

        await cog.gif(mock_ctx)
        mock_ctx.send.assert_called_once()
        args, kwargs = mock_ctx.send.call_args
        assert "embed" in kwargs
        assert kwargs["embed"].footer.text == "Source: Klipy"

@pytest.mark.asyncio
async def test_gif_command_fallback_to_giphy(mock_bot, mock_ctx):
    with patch.dict(os.environ, {"KLIPY_API_KEY": "test_klipy", "GIPHY_API_KEY": "test_giphy"}, clear=True):
        cog = Memes(mock_bot)
        cog.session = AsyncMock()
        
        klipy_resp = AsyncMock()
        klipy_resp.status = 500
        giphy_resp = AsyncMock()
        giphy_resp.status = 200
        giphy_resp.json = AsyncMock(return_value={
            "data": [{"title": "Giphy GIF", "images": {"original": {"url": "https://example.com/giphy.gif"}}}]
        })
        
        cog.session.get.side_effect = [klipy_resp, giphy_resp]

        await cog.gif(mock_ctx)
        mock_ctx.send.assert_called_once()
        args, kwargs = mock_ctx.send.call_args
        assert kwargs["embed"].footer.text == "Source: Giphy"
