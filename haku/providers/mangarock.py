from haku.provider import Provider, Helpers
from haku.downloader import Downloader
from haku.meta import Chapter, Page
from typing import List
from PIL import Image
import aiohttp
import json
import re
import io


def decode(buffer):
    if not buffer[0] == 69:
        return buffer

    result = bytearray(len(buffer) + 15)
    n = len(buffer) + 7

    result[0] = 82  # R
    result[1] = 73  # I
    result[2] = 70  # F
    result[3] = 70  # F
    result[7] = (n >> 24) & 255
    result[6] = (n >> 16) & 255
    result[5] = (n >> 8) & 255
    result[4] = 255 & n
    result[8] = 87  # W
    result[9] = 69  # E
    result[10] = 66  # B
    result[11] = 80  # P
    result[12] = 86  # V
    result[13] = 80  # P
    result[14] = 56  # 8

    for i in range(len(buffer)):
        result[i + 15] = 101 ^ buffer[i]

    return result


class MangarockDownloader(Downloader):

    async def _page(self, session: aiohttp.ClientSession, page: Page) -> Page:
        async with session.get(page.url) as response:
            raw = await response.read()
            stream = io.BytesIO(decode(raw))
            image = Image.open(stream)
            stream.close()
            return image


class Mangarock(Provider):
    name = 'mangarock'
    pattern = r'^https://mangarock.to'
    downloader = MangarockDownloader

    async def fetch_chapters(self, url: str, session: aiohttp.ClientSession) -> List[Chapter]:
        page = await Helpers.scrape_webpage(session, url)

        chapters = []
        for chapter in page.select('div.all-chapers tbody a'):
            meta = re.search(r'Vol.(\d*) *#(.*): *(.*)', chapter.text)

            volume = meta.group(1) if meta else None
            index = meta.group(2) if meta else ''
            title = meta.group(3) if meta else ''
            url = chapter['href']

            if index != '' and title != '':
                chapters.append(Chapter(
                    volume=volume,
                    index=index,
                    title=title,
                    url=url
                ))

        return chapters

    async def fetch_pages(self, chapter: Chapter, session: aiohttp.ClientSession) -> List[Page]:
        page = await Helpers.scrape_webpage(session, chapter.url)

        pages = []
        meta = re.search(r'var mangaData = (.*?);', str(page))
        for index, page in enumerate(json.loads(meta.group(1))):
            pages.append(Page(
                url=page['url'],
                index=str(index)
            ))

        return pages


provider = Mangarock
