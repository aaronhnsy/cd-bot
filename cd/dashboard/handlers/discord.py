# Future
from __future__ import annotations

# Standard Library
import abc
import binascii
import json
import os

# Local
from cd import config, exceptions, objects, utilities


__all__ = (
    "DiscordLogin",
)


class DiscordLogin(utilities.HTTPHandler, abc.ABC):

    async def get(self) -> None:  # type: ignore

        identifier = self.get_identifier()
        user_state = self.get_secure_cookie("state")
        auth_state = self.get_query_argument("state", None)
        code = self.get_query_argument("code", None)

        if not code or not auth_state or not user_state:

            state = binascii.hexlify(os.urandom(16)).decode()

            self.set_secure_cookie(
                "state",
                state
            )

            return self.redirect(
                f"https://discord.com/api/oauth2/authorize?"
                f"client_id={config.CLIENT_ID}&"
                f"response_type=code&"
                f"scope=identify%20guilds&"
                f"redirect_uri={config.REDIRECT_URI}&"
                f"state={state}"
            )

        if auth_state != user_state.decode():
            self.set_status(400)
            return await self.finish({"error": "user state and server state must match."})

        self.clear_cookie("state")

        async with self.bot.session.post(
                "https://discord.com/api/oauth2/token",
                data={
                    "client_secret": config.CLIENT_SECRET,
                    "client_id":     config.CLIENT_ID,
                    "redirect_uri":  config.REDIRECT_URI,
                    "code":          code,
                    "grant_type":    "authorization_code",
                    "scope":         "identify guilds",
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
        ) as response:
            if 200 < response.status > 206:
                raise exceptions.HTTPException(response, json.dumps(await response.json()))

            data = await response.json()

        if data.get("error"):
            raise exceptions.HTTPException(response, json.dumps(data))

        token_response = objects.Token(data)
        await self.bot.redis.hset("tokens", identifier, token_response.json)

        return self.redirect("/profile")
