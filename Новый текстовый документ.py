# meta developer: @chatgpt
# scope: hikka_only
# requires: hikka

import asyncio
import random
from datetime import datetime
from hikkatl.tl.types import Message
from .. import loader, utils

@loader.tds
class IrisFarm(loader.Module):
    """Автофарм ирис-коинов (фарма в @iris_cm_bot)"""

    strings = {
        "name": "IrisFarm",
        "on": "🌸 IrisFarm включён",
        "off": "🛑 IrisFarm выключен",
        "already_on": "⚠️ IrisFarm уже включён",
        "already_off": "⚠️ IrisFarm уже выключен",
        "status_on": "✅ IrisFarm: включён",
        "status_off": "❌ IrisFarm: выключен",
    }

    def __init__(self):
        self.task = None
        self.enabled = False

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        self.enabled = self.db.get(self.name, "enabled", False)
        self.total_farms = self.db.get(self.name, "total_farms", 0)
        self.last_farm = self.db.get(self.name, "last_farm", "—")

        if self.enabled:
            self.task = asyncio.create_task(self.farm_loop())

    async def farm_loop(self):
        while self.enabled:
            try:
                await self.client.send_message(
                    "iris_cm_bot",
                    "фарма"
                )

                self.total_farms += 1
                self.last_farm = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                self.db.set(self.name, "total_farms", self.total_farms)
                self.db.set(self.name, "last_farm", self.last_farm)

            except Exception:
                pass

            delay = random.randint(4 * 3600, 4 * 3600 + 600)
            await asyncio.sleep(delay)

    @loader.command()
    async def irisfarm(self, message: Message):
        """on/off/status/log — управление автофармом"""
        args = utils.get_args_raw(message).lower()

        if args == "on":
            if self.enabled:
                return await utils.answer(message, self.strings("already_on"))

            self.enabled = True
            self.db.set(self.name, "enabled", True)
            self.task = asyncio.create_task(self.farm_loop())
            return await utils.answer(message, self.strings("on"))

        elif args == "off":
            if not self.enabled:
                return await utils.answer(message, self.strings("already_off"))

            self.enabled = False
            self.db.set(self.name, "enabled", False)
            if self.task:
                self.task.cancel()
            return await utils.answer(message, self.strings("off"))

        elif args == "status":
            return await utils.answer(
                message,
                (
                    f"{self.strings('status_on')}\n"
                    f"🌾 Всего фармов: {self.total_farms}\n"
                    f"🕒 Последний: {self.last_farm}"
                ) if self.enabled else self.strings("status_off")
            )

        elif args == "log":
            return await utils.answer(
                message,
                f"📊 **IrisFarm — логи**\n\n"
                f"🌾 Всего фармов: {self.total_farms}\n"
                f"🕒 Последний фарм: {self.last_farm}"
            )

        else:
            await utils.answer(
                message,
                "Использование:\n"
                ".irisfarm on\n"
                ".irisfarm off\n"
                ".irisfarm status\n"
                ".irisfarm log"
            )
