# Future
from __future__ import annotations

# Standard Library
import functools
from collections.abc import Callable
from typing import TYPE_CHECKING, Concatenate, Literal, ParamSpec, TypeVar

# Packages
import humanize
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

# Local
from cd import exceptions, utilities


if TYPE_CHECKING:
    # Local
    from cd.bot import CD


__all__ = (
    "spotify",
    "edit_image",
    "do_edit_image",
)


T = TypeVar("T")
P = ParamSpec("P")


MAX_CONTENT_SIZE: int = (2 ** 20) * 25
VALID_CONTENT_TYPES: list[str] = ["image/gif", "image/heic", "image/jpeg", "image/png", "image/webp", "image/avif", "image/svg+xml"]


################
# EDIT METHODS #
################

def spotify(
    IMAGE: Image,
    length: float,
    elapsed: float,
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

    EXO_FONT = "cd/resources/Exo-Bold.ttf"

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
                    body=utilities.format_seconds(elapsed),
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
                body=utilities.format_seconds(length),
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
                        body=utilities.format_seconds(elapsed + (index // FPS)),
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


###########
# EXECUTE #
###########

async def edit_image(
    url: str,
    bot: CD,
    function: Callable[Concatenate[Image, P], None],
    *args: P.args,
    **kwargs: P.kwargs
) -> str:

    # request image bytes

    async with bot.session.get(url) as request:

        if request.status != 200:
            raise exceptions.EmbedError(description="Something went wrong while fetching that image.")

        if request.headers.get("Content-Type") not in VALID_CONTENT_TYPES:
            raise exceptions.EmbedError(description="That image format is not allowed.")

        if int(request.headers.get("Content-Length") or "0") > MAX_CONTENT_SIZE:
            raise exceptions.EmbedError(
                description=f"That image is too big to edit. The maximum file size is "
                            f"**{humanize.naturalsize(MAX_CONTENT_SIZE)}**."
            )

        original_bytes = await request.read()

    # edit image

    partial: functools.partial[tuple[bytes, str]] = functools.partial(do_edit_image, function, original_bytes, *args, **kwargs)
    try:
        edited_bytes, image_format = await bot.loop.run_in_executor(None, partial)
    except Exception:
        raise exceptions.EmbedError(description="Something went wrong while editing that image.")

    # upload image and return url

    return await utilities.upload_file(bot.session, fp=edited_bytes, format=image_format)


def do_edit_image(
    function: Callable[Concatenate[Image, P], None],
    image_bytes: bytes,
    *args: P.args,
    **kwargs: P.kwargs
) -> tuple[bytes, str]:

    with Image(blob=image_bytes) as image, Color("transparent") as transparent:

        assert isinstance(image.format, str)

        if image.format != "GIF":
            image.background_color = transparent
            function(image, *args, **kwargs)

        else:
            image.coalesce()
            image.iterator_reset()

            image.background_color = transparent
            function(image, *args, **kwargs)

            while image.iterator_next():
                image.background_color = transparent
                function(image, *args, **kwargs)

        edited_bytes: bytes | None = image.make_blob(format=image.format)
        if not edited_bytes:
            raise exceptions.EmbedError(description="Something went wrong while editing that image.")

        image_format: str = image.format

        return edited_bytes, image_format
