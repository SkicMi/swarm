import pytest
from unittest.mock import patch, MagicMock


class TestSentryConfig:
    def test_sentry_config_init_without_dsn(self):
        with patch.dict('os.environ', {'SENTRY_DSN': ''}, clear=False):
            from src.monitoring.sentry import SentryConfig
            config = SentryConfig()
            assert config.environment == "development"


    def test_sentry_config_with_env_vars(self):
        with patch.dict('os.environ', {
            'SENTRY_DSN': 'https://key@sentry.io/123',
            'ENVIRONMENT': 'production'
        }, clear=False):
            from src.monitoring.sentry import SentryConfig
            config = SentryConfig()
            assert 'sentry.io' in config.dsn
            assert config.environment == 'production'

    def test_sentry_config_sample_rates(self):
        from src.monitoring.sentry import SentryConfig
        config = SentryConfig(sample_rate=0.5, traces_sample_rate=0.2)
        assert config.sample_rate == 0.5
        assert config.traces_sample_rate == 0.2


class TestPrometheusMetrics:
    def test_prometheus_port(self):
        from src.monitoring.prometheus import PROMETHEUS_PORT
        assert PROMETHEUS_PORT == 9090

    def test_setup_metrics_routes(self):
        from src.monitoring.prometheus import setup_metrics_routes
        assert callable(setup_metrics_routes)



class TestInitMonitoring:
    def test_init_monitoring_disabled_by_env(self):
        with patch.dict('os.environ', {'MONITORING_ENABLED': 'false'}, clear=False):
            import src.monitoring as mon
            mon.MONITORING_ENABLED = False
            result = mon.init_monitoring(enable_sentry=False)
            assert result is None

    def test_prometheus_port_env_var(self):
        with patch.dict('os.environ', {'PROMETHEUS_PORT': '8080'}, clear=False):
            from importlib import reload
            import src.monitoring.prometheus as prom
            reload(prom)
            assert prom.PROMETHEUS_PORT == 8080


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


class TestTelegramHub:
    def test_hub_creation(self):
        from src.telegram import TelegramHub
        hub = TelegramHub()
        assert hub.bots == {}

    def test_register_bot(self):
        from src.telegram import TelegramHub, BotPurpose
        hub = TelegramHub()
        hub.register_bot("test_bot", "token123", "chat123", BotPurpose.GENERAL)
        assert "test_bot" in hub.bots
        assert hub.bots["test_bot"].token == "token123"

    def test_get_bot_not_registered(self):
        from src.telegram import TelegramHub
        hub = TelegramHub()
        with pytest.raises(ValueError, match="not registered"):
            hub.get_bot("nonexistent")

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
