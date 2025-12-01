"""Utilities for downloading Apple Music content using gamdl.

This script demonstrates how to set up the gamdl downloaders and fetch
audio or video assets from Apple Music. It expects a Netscape-format
cookies.txt file that includes an authenticated Apple Music session.
"""

import argparse
import asyncio
import os
from pathlib import Path


def validate_cookies_path(cookies_path: str | Path | None = None) -> Path:
    """Resolve and validate the Netscape-format cookies file.

    The search order is:
    1. Explicit ``cookies_path`` argument.
    2. ``APPLE_MUSIC_COOKIES`` environment variable.
    3. ``cookies.txt`` in the current working directory.
    4. ``cookies.txt`` next to this script.
    """

    candidates: list[Path] = []

    if cookies_path is not None:
        candidates.append(Path(cookies_path))
    else:
        env_path = os.environ.get("APPLE_MUSIC_COOKIES")
        if env_path:
            candidates.append(Path(env_path))

        candidates.append(Path("cookies.txt"))
        candidates.append(Path(__file__).with_name("cookies.txt"))

    for path in candidates:
        resolved = path.resolve()
        if resolved.is_file():
            return resolved

    searched_locations = "\n - ".join(str(path.resolve()) for path in candidates)
    raise FileNotFoundError(
        "Missing Apple Music cookies file. Provide a Netscape-format "
        "cookies.txt via the --cookies flag, APPLE_MUSIC_COOKIES environment "
        "variable, or by placing cookies.txt in one of the searched locations:\n"
        f" - {searched_locations}"
    )


DEFAULT_APPLE_MUSIC_URL = (
    "https://music.apple.com/us/album/never-gonna-give-you-up-2022-remaster/1624945511?i=1624945512"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Apple Music content using gamdl")
    parser.add_argument(
        "--cookies",
        "-c",
        help=(
            "Path to a Netscape-format cookies.txt file. Overrides the APPLE_MUSIC_COOKIES "
            "environment variable and the default search locations."
        ),
    )
    parser.add_argument(
        "--url",
        "-u",
        default=DEFAULT_APPLE_MUSIC_URL,
        help="Apple Music URL for the track or video to download.",
    )
    return parser.parse_args()


async def main(cookies: str | Path | None = None, url: str = DEFAULT_APPLE_MUSIC_URL) -> None:
    """Download content from Apple Music using the gamdl library.

    This function wires together the gamdl API clients, interfaces, and
    downloader implementations to download a single piece of content
    identified by its Apple Music URL. Update the URL passed to
    ``downloader.get_url_info`` to target a different track or video.
    """

    from gamdl.api import AppleMusicApi, ItunesApi
    from gamdl.downloader import (
        AppleMusicBaseDownloader,
        AppleMusicDownloader,
        AppleMusicMusicVideoDownloader,
        AppleMusicSongDownloader,
        AppleMusicUploadedVideoDownloader,
    )
    from gamdl.interface import (
        AppleMusicInterface,
        AppleMusicMusicVideoInterface,
        AppleMusicSongInterface,
        AppleMusicUploadedVideoInterface,
    )

    # Initialize APIs
    cookies_path = validate_cookies_path(cookies)

    apple_music_api = AppleMusicApi.from_netscape_cookies(cookies_path=str(cookies_path))
    await apple_music_api.setup()

    itunes_api = ItunesApi(
        apple_music_api.storefront,
        apple_music_api.language,
    )
    itunes_api.setup()

    # Initialize interfaces
    interface = AppleMusicInterface(apple_music_api, itunes_api)
    song_interface = AppleMusicSongInterface(interface)
    music_video_interface = AppleMusicMusicVideoInterface(interface)
    uploaded_video_interface = AppleMusicUploadedVideoInterface(interface)

    # Initialize base downloader
    base_downloader = AppleMusicBaseDownloader()
    base_downloader.setup()

    # Initialize specialized downloaders
    song_downloader = AppleMusicSongDownloader(
        base_downloader=base_downloader,
        interface=song_interface,
    )
    music_video_downloader = AppleMusicMusicVideoDownloader(
        base_downloader=base_downloader,
        interface=music_video_interface,
    )
    uploaded_video_downloader = AppleMusicUploadedVideoDownloader(
        base_downloader=base_downloader,
        interface=uploaded_video_interface,
    )

    # Create main downloader
    downloader = AppleMusicDownloader(
        interface=interface,
        base_downloader=base_downloader,
        song_downloader=song_downloader,
        music_video_downloader=music_video_downloader,
        uploaded_video_downloader=uploaded_video_downloader,
    )

    # Download a song
    url_info = downloader.get_url_info(url)

    if url_info:
        download_queue = await downloader.get_download_queue(url_info)
        if download_queue:
            for download_item in download_queue:
                await downloader.download(download_item)


if __name__ == "__main__":
    cli_args = parse_args()
    asyncio.run(main(cookies=cli_args.cookies, url=cli_args.url))
