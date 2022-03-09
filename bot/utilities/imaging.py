# Future
from __future__ import annotations

# Standard Library
import multiprocessing
import sys
import time
import traceback
from multiprocessing.connection import Connection
from typing import Any, Callable, Literal

# Packages
import aiohttp
import humanize
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

# My stuff
from core import values
from utilities import custom, exceptions, objects, utils


MAX_CONTENT_SIZE: int = (2 ** 20) * 25
VALID_CONTENT_TYPES: list[str] = ["image/gif", "image/heic", "image/jpeg", "image/png", "image/webp", "image/avif", "image/svg+xml"]


def spotify(
    IMAGE: Image,
    length: int,
    elapsed: int,
    title: str,
    artists: list[str],
    format: Literal["png", "gif", "smooth_gif"]
) -> None:  # sourcery skip: extract-duplicate-method, extract-method

    if format == "gif":
        IMAGE.format = "gif"
        FRAMES = 50
        DELAY = 20
        FPS = 100 / DELAY
    elif format == "smooth_gif":
        IMAGE.format = "gif"
        FRAMES = 500
        DELAY = 2
        FPS = 100 / DELAY
    else:
        IMAGE.format = "png"
        FRAMES = 0
        DELAY = 0
        FPS = 0

    ###################
    # PIXEL VARIABLES #
    ###################
    COVER_WIDTH = 150
    COVER_HEIGHT = 150
    COVER_PASTE_OFFSET = 25

    IMAGE_WIDTH = 500
    IMAGE_HEIGHT = 500
    IMAGE_CROP_OFFSET = 150

    IMAGE_BLUR_STRENGTH = 10

    TRACK_INFO_START_X = COVER_WIDTH + (COVER_PASTE_OFFSET * 2)

    PROGRESS_BAR_LENGTH = (IMAGE_WIDTH - COVER_PASTE_OFFSET) - TRACK_INFO_START_X
    PROGRESS_BAR_HEIGHT = 5
    PROGRESS_BAR_Y1 = 140
    PROGRESS_BAR_Y2 = PROGRESS_BAR_Y1 + PROGRESS_BAR_HEIGHT

    #########################################
    # TEXT / COLOUR / FONT / SIZE VARIABLES #
    #########################################
    TRANSPARENT = Color("transparent")
    BLACK = Color("black")
    GRAY = Color("#565859")
    WHITE = Color("#FFFFFF")

    EXO_FONT = "resources/Exo-Bold.ttf"

    TITLE_FONT_SIZE = 20
    ARTISTS_FONT_SIZE = 15

    #########
    # COVER #
    #########
    with IMAGE.clone() as COVER, Image(width=COVER_WIDTH, height=COVER_HEIGHT, background=TRANSPARENT) as MASK:

        ##############
        # EDIT COVER #
        ##############
        COVER.resize(
            width=COVER_WIDTH,
            height=COVER_HEIGHT
        )

        #############
        # DRAW MASK #
        #############
        with Drawing() as DRAW:
            DRAW.fill_color = BLACK
            DRAW.rectangle(
                left=0,
                top=0,
                width=COVER_WIDTH,
                height=COVER_HEIGHT,
                xradius=COVER_WIDTH,
                yradius=COVER_HEIGHT
            )
            DRAW(MASK)

        #############
        # EDIT BASE #
        #############
        IMAGE.resize(
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT
        )
        IMAGE.crop(
            top=IMAGE_CROP_OFFSET,
            bottom=IMAGE_HEIGHT - IMAGE_CROP_OFFSET,
        )
        IMAGE.blur(
            sigma=IMAGE_BLUR_STRENGTH
        )

        #############
        # DRAW INFO #
        #############
        with Drawing() as DRAW:

            DRAW.font = EXO_FONT
            DRAW.text_antialias = True

            # draw progress bar base
            DRAW.fill_color = GRAY
            DRAW.rectangle(
                left=TRACK_INFO_START_X,
                right=TRACK_INFO_START_X + PROGRESS_BAR_LENGTH,
                top=PROGRESS_BAR_Y1,
                bottom=PROGRESS_BAR_Y2,
                radius=IMAGE.width * 0.003
            )
            DRAW.fill_color = WHITE

            if format == "png":

                # draw progress bar fill
                DRAW.rectangle(
                    left=TRACK_INFO_START_X,
                    right=TRACK_INFO_START_X + (PROGRESS_BAR_LENGTH * (elapsed / length)),
                    top=PROGRESS_BAR_Y1,
                    bottom=PROGRESS_BAR_Y2,
                    radius=IMAGE.width * 0.003
                )

                # draw track elapsed time
                DRAW.text(
                    x=TRACK_INFO_START_X,
                    y=PROGRESS_BAR_Y1 - PROGRESS_BAR_HEIGHT,
                    body=utils.format_seconds(elapsed),
                )

                # paste mask onto cover.
                COVER.composite_channel(
                    channel="alpha",
                    image=MASK,
                    operator="copy_alpha",
                    left=0,
                    top=0
                )

                # paste cover onto frame
                IMAGE.composite(
                    image=COVER,
                    left=COVER_PASTE_OFFSET,
                    top=COVER_PASTE_OFFSET
                )

            # draw track length
            DRAW.text_alignment = "right"
            DRAW.text(
                x=TRACK_INFO_START_X + PROGRESS_BAR_LENGTH,
                y=PROGRESS_BAR_Y1 - PROGRESS_BAR_HEIGHT,
                body=utils.format_seconds(length),
            )
            DRAW.text_alignment = "left"

            # draw track title
            DRAW.font_size = TITLE_FONT_SIZE
            DRAW.text(
                x=TRACK_INFO_START_X,
                y=75,
                body=title,
            )

            # draw track artists
            DRAW.font_size = ARTISTS_FONT_SIZE
            DRAW.text(
                x=TRACK_INFO_START_X,
                y=95,
                body=", ".join(artists),
            )

            DRAW(IMAGE)

        if format != "png":

            #######################
            # CREATE IMAGE FRAMES #
            #######################
            IMAGE.sequence.extend([IMAGE.clone() for _ in range(FRAMES)])

            #####################
            # EDIT IMAGE FRAMES #
            #####################

            IMAGE.iterator_reset()

            # iterate through frames
            while IMAGE.iterator_next():

                index = IMAGE.iterator_get() - 1

                with COVER.clone() as COVER_CLONE:

                    # rotate cover
                    COVER_CLONE.distort(
                        "scale_rotate_translate",
                        (
                            COVER_WIDTH / 2,
                            COVER_HEIGHT / 2,
                            (index * (360 / (FPS * 5)))
                        )
                    )

                    # paste mask onto cover.
                    COVER_CLONE.composite_channel(
                        channel="alpha",
                        image=MASK,
                        operator="copy_alpha",
                        left=0,
                        top=0
                    )

                    # paste cover onto frame
                    IMAGE.composite(
                        image=COVER_CLONE,
                        left=COVER_PASTE_OFFSET,
                        top=COVER_PASTE_OFFSET
                    )

                with Drawing() as DRAW:

                    DRAW.font = EXO_FONT
                    DRAW.text_antialias = True
                    DRAW.fill_color = WHITE

                    # draw progress bar fill
                    DRAW.rectangle(
                        left=TRACK_INFO_START_X,
                        right=TRACK_INFO_START_X + (PROGRESS_BAR_LENGTH * ((elapsed + (index // FPS)) / length)),
                        top=PROGRESS_BAR_Y1,
                        bottom=PROGRESS_BAR_Y2,
                        radius=IMAGE.width * 0.003
                    )

                    # draw track elapsed time
                    DRAW.text(
                        x=TRACK_INFO_START_X,
                        y=PROGRESS_BAR_Y1 - PROGRESS_BAR_HEIGHT,
                        body=utils.format_seconds(elapsed + (index // FPS)),
                    )

                    DRAW(IMAGE)

                IMAGE.delay = DELAY

            ######################
            # DELETE FIRST FRAME #
            ######################
            del IMAGE.sequence[0]

    ############
    # OPTIMIZE #
    ############
    if format != "png":
        IMAGE.optimize_transparency()


async def request_image_bytes(*, session: aiohttp.ClientSession, url: str) -> bytes:

    async with session.get(url) as request:

        if request.status != 200:
            raise exceptions.EmbedError(description="Something went wrong while fetching that image.")

        if request.headers.get("Content-Type") not in VALID_CONTENT_TYPES:
            raise exceptions.EmbedError(description="That image format is not allowed.")

        if int(request.headers.get("Content-Length") or "0") > MAX_CONTENT_SIZE:
            raise exceptions.EmbedError(description=f"That image is too big to edit. The maximum file size is **{humanize.naturalsize(MAX_CONTENT_SIZE)}**.")

        return await request.read()


async def edit_image(ctx: custom.Context, edit_function: Callable[..., Any], image: objects.FakeImage, **kwargs: Any) -> str:

    _download_image_start = time.perf_counter()
    image_bytes = await request_image_bytes(session=ctx.bot.session, url=image.url)
    _download_image_end = time.perf_counter()

    _edit_image_start = time.perf_counter()

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
        raise exceptions.EmbedError(description="Something went wrong while editing that image.")

    _edit_image_end = time.perf_counter()

    _upload_image_start = time.perf_counter()
    url = await utils.upload_file(ctx.bot.session, file=data[0], format=data[1])
    _upload_image_end = time.perf_counter()

    _download = (_download_image_end - _download_image_start) * 1000
    _edit = (_edit_image_end - _edit_image_start) * 1000
    _upload = (_upload_image_end - _upload_image_start) * 1000

    await ctx.send(
        f"Download: **{_download:.2f}ms**\n"
        f"Edit: **{_edit:.2f}ms**\n"
        f"Upload: **{_upload:.2f}ms**\n"
        f"Total: **{(_download + _edit + _upload):.2f}ms**",
    )

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

            edited_image_format = image.format
            edited_image_bytes = image.make_blob()  # type: ignore

            pipe.send((edited_image_bytes, edited_image_format))

    except Exception as error:
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)), file=sys.stderr)
        pipe.send(ValueError)
