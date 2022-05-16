# Future
from __future__ import annotations

# Standard Library
import abc
import asyncio
import json
from typing import Any

# Packages
import slate
import tornado.web
import tornado.websocket

# Local
from cd import config, custom, exceptions, objects, utilities


__all__ = (
    "WebSocket",
)


# noinspection PyAttributeOutsideInit
class WebSocket(utilities.WebSocketHandler, abc.ABC):

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

    async def on_message(self, message: str | bytes) -> None:  # sourcery no-metrics

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
            )

            # Get token to make sure identifier is valid

            token_data = await self.bot.redis.hget("tokens", identifier or "")
            if not token_data:
                return self.close(code=4007, reason="You must login with the site at least once.")

            token = objects.Token(json.loads(token_data))

            if token.has_expired:

                async with self.bot.session.post(
                        url="https://discord.com/api/oauth2/token",
                        data={
                            "client_secret": config.CLIENT_SECRET,
                            "client_id":     config.CLIENT_ID,
                            "redirect_uri":  config.REDIRECT_URI,
                            "refresh_token": token.refresh_token,
                            "grant_type":    "refresh_token",
                            "scope":         "identify guilds",
                        },
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                ) as response:

                    if 200 < response.status > 206:
                        raise exceptions.HTTPException(response, json.dumps(await response.json()))

                    token_data = await response.json()

                if token_data.get("error"):
                    raise exceptions.HTTPException(response, json.dumps(token_data))

                token = objects.Token(token_data)

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
    def _track_to_dict(track: slate.Track) -> dict[str, Any]:

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

            voice_client: custom.Player | None = self.guild.voice_client  # type: ignore

            if voice_client and voice_client.current:
                await self.write_message(
                    {
                        "op":   2,
                        "data": {
                            "type":     "POSITION_UPDATE",
                            "position": voice_client.position,
                            "track": {
                                "length": voice_client.current.length
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

        voice_client: custom.Player | None = self.guild.voice_client  # type: ignore

        if voice_client:
            data["track"] = self._track_to_dict(voice_client.current) if voice_client.current else None
            data["position"] = voice_client.position
            data["paused"] = voice_client.is_paused()
            data["connected"] = voice_client.is_connected()

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "IDENTIFIED",
                    **data
                }
            }
        )

    async def _handle_player_update(self, voice_client: custom.Player) -> None:

        if voice_client.channel.guild.id != self.guild_id:
            return

        data: dict[str, Any] = {
            "track":     None,
            "position":  None,
            "paused":    None,
            "connected": None
        }

        if voice_client:
            data["track"] = self._track_to_dict(voice_client.current) if voice_client.current else None
            data["position"] = voice_client.position
            data["paused"] = voice_client.is_paused()
            data["connected"] = voice_client.is_connected()

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "PLAYER_UPDATE",
                    **data
                }
            }
        )

    async def _handle_track_end(self, voice_client: custom.Player) -> None:

        if voice_client.channel.guild.id != self.guild_id:
            return

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "TRACK_END",
                }
            }
        )

    async def _handle_player_disconnect(self, voice_client: custom.Player) -> None:

        if voice_client.channel.guild.id != self.guild_id:
            return

        await self.write_message(
            {
                "op":   2,
                "data": {
                    "type": "PLAYER_DISCONNECT",
                }
            }
        )
