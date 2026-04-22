import pytest
from unittest.mock import patch, AsyncMock


class TestTelegramBotConfig:
    def test_bot_config_defaults(self):
        from src.telegram import TelegramBotConfig, BotPurpose
        config = TelegramBotConfig(
            token="test_token",
            chat_id="123456",
            purpose=BotPurpose.GENERAL,
        )
        assert config.token == "test_token"
        assert config.chat_id == "123456"
        assert config.purpose == BotPurpose.GENERAL
        assert config.name == ""



class TestTelegramHub:
    def test_hub_creation(self):
        from src.telegram import TelegramHub
        hub = TelegramHub()
        assert hub.bots == {}
        assert hub._instances == {}


    def test_register_bot(self):
        from src.telegram import TelegramHub, BotPurpose
        hub = TelegramHub()
        hub.register_bot("test_bot", "token123", "chat123", BotPurpose.GENERAL)
        assert "test_bot" in hub.bots
        assert hub.bots["test_bot"].token == "token123"
        assert hub.bots["test_bot"].chat_id == "chat123"

    def test_get_bot_not_registered(self):
        from src.telegram import TelegramHub
        hub = TelegramHub()
        with pytest.raises(ValueError, match="not registered"):
            hub.get_bot("nonexistent")

    @patch('src.telegram.Bot')
    def test_get_bot_returns_cached(self, mock_bot_class):
        from src.telegram import TelegramHub, BotPurpose
        hub = TelegramHub()
        hub.register_bot("test_bot", "token123", "chat123", BotPurpose.GENERAL)
        bot1 = hub.get_bot("test_bot")
        bot2 = hub.get_bot("test_bot")
        assert bot1 is bot2

    def test_get_hub_singleton(self):
        from src.telegram import get_hub, TelegramHub
        hub1 = get_hub()
        hub2 = get_hub()
        assert isinstance(hub1, TelegramHub)
        assert hub1 is hub2


class TestBotPurpose:
    def test_bot_purpose_values(self):
        from src.telegram import BotPurpose
        assert BotPurpose.GENERAL.value == "general"
        assert BotPurpose.ALERTS.value == "alerts"
        assert BotPurpose.REPORTS.value == "reports"
        assert BotPurpose.COMMANDS.value == "commands"



class TestInitTelegram:
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': '123456'})
    def test_init_telegram_with_env(self):
        from src.telegram import init_telegram, get_hub
        hub = init_telegram()
        assert "default" in hub.bots
        assert "alerts" in hub.bots
        assert "reports" in hub.bots

    def test_init_telegram_explicit_params(self):
        from src.telegram import init_telegram, get_hub
        import src.telegram as tg
        tg._hub = None
        hub = init_telegram(default_token="explicit_token", default_chat_id="explicit_chat")
        assert hub.bots["default"].token == "explicit_token"
        assert hub.bots["default"].chat_id == "explicit_chat"
