from __future__ import annotations

import abc
import asyncio
import json
from typing import Any

import discord
import tornado.web
import tornado.websocket

from discord.ext import lava
from cd import config, custom
from cd.modules import dashboard, voice
from cd.modules.dashboard.utilities import handlers


__all__ = (
    "WebSocket",
)


# noinspection PyAttributeOutsideInit
class WebSocket(handlers.WebSocketHandler, abc.ABC):

    # Overrides

    async def open(self) -> None:  # type: ignore

        self.authenticated = False
        await self._send_identify_request()

    async def on_authenticated(self) -> None:

        self.authenticated = True
        await self._handle_identified()

        self.bot.add_listener(self._handle_player_update, "on_dashboard_player_connect")
        self.bot.add_listener(self._handle_player_disconnect, "on_dashboard_player_disconnect")
        self.bot.add_listener(self._handle_player_update, "on_dashboard_track_start")
        self.bot.add_listener(self._handle_track_end, "on_dashboard_track_end")

        self._position_update_task = asyncio.create_task(self._position_update_loop())

    def on_close(self) -> None:

        self.bot.remove_listener(self._handle_player_update, "on_dashboard_player_connect")
        self.bot.remove_listener(self._handle_player_disconnect, "on_dashboard_player_disconnect")
        self.bot.remove_listener(self._handle_player_update, "on_dashboard_track_start")
        self.bot.remove_listener(self._handle_track_end, "on_dashboard_track_end")

        self._position_update_task.cancel()

    async def on_message(self, message: str | bytes) -> None:  # sourcery skip low-code-quality

        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            return self.close(code=4001, reason="Payload is not valid JSON.")

        op = payload.get("op")

        # op: <HELLO: 0>
        if op == 0:
            return self.close(code=4003, reason="Op code <HELLO: O> is only sent by the server.")

        # op: <IDENTIFY: 1>
        elif op == 1:

            if self.authenticated is True:
                return self.close(code=4004, reason="You are already authenticated.")

            data = payload.get("data")

            # Check for keys

            guild_id = data.get("guild_id")
            if not guild_id:
                return self.close(code=4005, reason="No 'guild_id' key provided.")

            identifier = data.get("identifier")
            if not identifier:
                return self.close(code=4005, reason="No 'identifier' key provided.")

            # Check guild exists

            guild = self.bot.get_guild(int(guild_id)) if guild_id else None
            if not guild:
                return self.close(code=4006, reason=f"Guild with id '{guild_id}' not found.")

            self.guild_id = int(guild_id)
            self.guild = guild

            # decrypt identifier

            identifier = tornado.web.decode_signed_value(
                secret=self.application.settings["cookie_secret"],
                name="identifier",
                value=identifier.strip("\"")
            ) or ""

            # Get token to make sure identifier is valid

            token_data: str | None = await self.bot.redis.hget("tokens", identifier)
            if not token_data:
                return self.close(code=4007, reason="You must login with the site at least once.")

            token = dashboard.Token(json.loads(token_data))

            if token.has_expired:

                async with self.bot.session.post(
                        url="https://discord.com/api/oauth2/token",
                        data={
                            "client_secret": config.DISCORD_CLIENT_SECRET,
                            "client_id":     config.DISCORD_CLIENT_ID,
                            "redirect_uri":  config.DASHBOARD_REDIRECT_URL,
                            "refresh_token": token.refresh_token,
                            "grant_type":    "refresh_token",
                            "scope":         "identify guilds",
                        },
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                ) as response:

                    if 200 < response.status > 206:
                        raise discord.HTTPException(response, json.dumps(await response.json()))

                    data = await response.json()

                if data.get("error"):
                    raise discord.HTTPException(response, json.dumps(token_data))

                token = dashboard.Token(data)

                await self.bot.redis.hset(
                    "tokens",
                    identifier,
                    token.json
                )

            await self.on_authenticated()

        # op: <DISPATCH: 2>
        elif op == 2:
            return self.close(code=4003, reason="Op code <DISPATCH: 2> is only sent by the server.")

        else:
            return self.close(code=4002, reason="OP code not recognized.")

    # Utilities

    @staticmethod
    def _track_to_dict(track: lava.Track) -> dict[str, Any]:

        ctx: custom.Context = track.extras["ctx"]

        return {
            "title":       track.title,
            "author":      track.author,
            "uri":         track.uri,
            "identifier":  track.identifier,
            "length":      track.length,
            "source":      track.source.name,
            "artwork_url": track.artwork_url,
            "requester":   ctx.author.name,
        }

    # Tasks

    async def _position_update_loop(self) -> None:

        while True:

            player: voice.Player | None = self.guild.voice_client  # type: ignore

            if player and player.current:
                await self.write_message(
                    {
                        "op":   2,
                        "data": {
                            "type":     "POSITION_UPDATE",
                            "position": player.position,
                            "track":    {
                                "length": player.current.length
                            }
                        }
                    }
                )

            await asyncio.sleep(1)

    # Handlers

    async def _send_identify_request(self) -> None:
        return await self.write_message(
            {
                "op":   0,
                "data": {
                    "message": "Waiting for op: <IDENTIFY: 1>"
                }
            }
        )

    async def _handle_identified(self) -> None:

        data: dict[str, Any] = {
            "track":     None,
            "position":  None,
            "paused":    None,
            "connected": None
        }

        player: voice.Player | None = self.guild.voice_client  # type: ignore

        if player:
            data["track"] = self._track_to_dict(player.current) if player.current else None
            data["position"] = player.position
            data["paused"] = player.is_paused()
            data["connected"] = player.is_connected()

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "IDENTIFIED",
                    **data
                }
            }
        )

    async def _handle_player_update(self, player: voice.Player) -> None:

        if player.channel.guild.id != self.guild_id:
            return

        data: dict[str, Any] = {
            "track":     None,
            "position":  None,
            "paused":    None,
            "connected": None
        }

        if player:
            data["track"] = self._track_to_dict(player.current) if player.current else None
            data["position"] = player.position
            data["paused"] = player.is_paused()
            data["connected"] = player.is_connected()

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "PLAYER_UPDATE",
                    **data
                }
            }
        )

    async def _handle_track_end(self, player: voice.Player) -> None:

        if player.channel.guild.id != self.guild_id:
            return

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "TRACK_END",
                }
            }
        )

    async def _handle_player_disconnect(self, player: voice.Player) -> None:

        if player.channel.guild.id != self.guild_id:
            return

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "PLAYER_DISCONNECT",
                }
            }
        )
