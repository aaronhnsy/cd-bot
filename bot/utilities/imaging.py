# Future
from __future__ import annotations

# Standard Library
import multiprocessing
import sys
import traceback
from multiprocessing.connection import Connection
from typing import Any, Callable

# Packages
import aiohttp
import humanize
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

# My stuff
from core import values
from utilities import custom, exceptions, objects, utils


def spotify(
    image: Image,
    length: int,
    elapsed: int,
    title: str,
    artists: list[str],
) -> None:  # sourcery skip: extract-method

    image.format = "png"

    with image.clone() as cover:

        # size cover appropriately.
        cover.resize(width=150, height=150)

        # create and apply rounded mask to cover.
        with Image(width=cover.width, height=cover.height, background=Color("transparent")) as mask:

            with Drawing() as draw:
                draw.fill_color = Color("black")
                draw.rectangle(
                    left=0,
                    top=0,
                    right=mask.width,
                    bottom=mask.height,
                    radius=mask.width
                )
                draw(mask)

            cover.composite_channel(
                channel="alpha",
                image=mask,
                operator="copy_alpha",
                left=0,
                top=0
            )

        # resize base image, crop it, blur it, and then paste cover onto it.
        image.resize(width=500, height=500)
        image.crop(top=150, bottom=350)
        image.blur(sigma=10)
        image.composite(cover, left=25, top=25)

    with Drawing() as draw:

        draw.font = "resources/Exo-Bold.ttf"

        # Progress bar base
        draw.fill_color = Color("#565859")
        draw.rectangle(
            left=200,
            right=475,
            top=140,
            bottom=145,
            radius=image.width * 0.003
        )

        # Progress bar fill
        draw.fill_color = Color("#ffffff")
        draw.rectangle(
            left=200,
            right=225 + (250 * (elapsed / length)),
            top=140,
            bottom=145,
            radius=image.width * 0.003
        )

        # Elapsed time
        draw.text(
            x=200,
            y=135,
            body=utils.format_seconds(elapsed),
        )

        # Length
        draw.text_alignment = "right"
        draw.text(
            x=475,
            y=135,
            body=utils.format_seconds(length),
        )
        draw.text_alignment = "left"

        # Title
        draw.font_size = 20
        draw.text(
            x=200,
            y=75,
            body=title,
        )

        # Artists
        draw.font_size = 15
        draw.text(
            x=200,
            y=95,
            body=", ".join(artists),
        )

        draw(image)


MAX_CONTENT_SIZE = (2 ** 20) * 25
VALID_CONTENT_TYPES = ["image/gif", "image/heic", "image/jpeg", "image/png", "image/webp", "image/avif", "image/svg+xml"]


async def request_image_bytes(*, session: aiohttp.ClientSession, url: str) -> bytes:

    async with session.get(url) as request:

        if request.status != 200:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="something went wrong while fetching that image."
            )

        if request.headers.get("Content-Type") not in VALID_CONTENT_TYPES:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="image format is not allowed.",
            )

        if int(request.headers.get("Content-Length") or "0") > MAX_CONTENT_SIZE:
            raise exceptions.EmbedError(
                colour=values.RED,
                description=f"image is too big to edit. maximum file size is **{humanize.naturalsize(MAX_CONTENT_SIZE)}**.",
            )

        return await request.read()


async def edit_image(ctx: custom.Context, edit_function: Callable[..., Any], image: objects.FakeImage, **kwargs: Any) -> str:

    image_bytes = await request_image_bytes(session=ctx.bot.session, url=image.url)
    receiving_pipe, sending_pipe = multiprocessing.Pipe(duplex=False)

    process = multiprocessing.Process(target=do_edit_image, daemon=True, args=(edit_function, image_bytes, sending_pipe), kwargs=kwargs)
    process.start()

    data = await ctx.bot.loop.run_in_executor(None, receiving_pipe.recv)
    process.join()

    receiving_pipe.close()
    sending_pipe.close()
    process.terminate()
    process.close()

    if data in (ValueError, EOFError):
        raise exceptions.EmbedError(
            colour=values.RED,
            description="something went wrong while editing that image."
        )

    url = await utils.upload_file(ctx.bot.session, file=data[0], format=data[1])
    del data

    return url


def do_edit_image(edit_function: Callable[..., Any], image_bytes: bytes, pipe: Connection, **kwargs: Any) -> None:

    try:
        with Image(blob=image_bytes) as image, Color("transparent") as transparent:

            if image.format != "GIF":
                image.background_color = transparent
                edit_function(image, **kwargs)

            else:
                image.coalesce()
                image.iterator_reset()

                image.background_color = transparent
                edit_function(image, **kwargs)
                while image.iterator_next():
                    image.background_color = transparent
                    edit_function(image, **kwargs)

                image.optimize_transparency()

            edited_image_format = image.format
            edited_image_bytes = image.make_blob()  # type: ignore

            pipe.send((edited_image_bytes, edited_image_format))

    except Exception as error:
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)), file=sys.stderr)
        pipe.send(ValueError)
