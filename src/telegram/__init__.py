"""
Telegram Hub for Project Swarm
==============================
Multi-bot Telegram notification and command handling.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message


class BotPurpose(Enum):
    GENERAL = "general"
    ALERTS = "alerts"
    REPORTS = "reports"
    COMMANDS = "commands"


@dataclass
class TelegramBotConfig:
    token: str
    chat_id: str
    purpose: BotPurpose
    name: str = ""


@dataclass
class TelegramHub:
    bots: dict[str, TelegramBotConfig] = field(default_factory=dict)
    _instances: dict[str, Bot] = field(default_factory=dict)
    _dispatcher: Dispatcher | None = None

    def register_bot(self, name: str, token: str, chat_id: str, purpose: BotPurpose) -> None:
        config = TelegramBotConfig(
            token=token,
            chat_id=chat_id,
            purpose=purpose,
            name=name,
        )
        self.bots[name] = config

    def get_bot(self, name: str = "default") -> Bot:
        if name not in self._instances:
            config = self.bots.get(name)
            if not config:
                raise ValueError(f"Bot {name} not registered")
            self._instances[name] = Bot(
                token=config.token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )
        return self._instances[name]

    async def send_message(
        self,
        text: str,
        bot_name: str = "default",
        parse_mode: str = "HTML",
        disable_notification: bool = False,
    ) -> Message:
        bot = self.get_bot(bot_name)
        config = self.bots[bot_name]
        return await bot.send_message(
            chat_id=config.chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
        )

    async def send_alert(self, text: str) -> Message:
        return await self.send_message(text, bot_name="alerts")

    async def send_report(self, text: str) -> Message:
        return await self.send_message(text, bot_name="reports")

    def setup_commands(self, commands: dict[str, Callable]) -> None:
        for command, handler in commands.items():
            for bot_config in self.bots.values():
                if bot_config.purpose == BotPurpose.COMMANDS:
                    pass


_hub: TelegramHub | None = None


def get_hub() -> TelegramHub:
    global _hub
    if _hub is None:
        _hub = TelegramHub()
    return _hub


def init_telegram(
    default_token: str | None = None,
    default_chat_id: str | None = None,
) -> TelegramHub:
    hub = get_hub()
    token = default_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = default_chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
    if token and chat_id:
        hub.register_bot("default", token, chat_id, BotPurpose.GENERAL)
        hub.register_bot("alerts", token, chat_id, BotPurpose.ALERTS)
        hub.register_bot("reports", token, chat_id, BotPurpose.REPORTS)
    return hub


__all__ = [
    "TelegramHub",
    "TelegramBotConfig",
    "BotPurpose",
    "get_hub",
    "init_telegram",
]
