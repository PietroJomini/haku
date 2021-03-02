from haku.provider import Provider
from haku.meta import Chapter, Page
from typing import List
import aiohttp
import re


# TODO(me) switch images server


class ManganeloCom(Provider):
    """Manganelo.com provider"""

    name = 'manganelo.com'
    pattern = r'^https://manganelo.com'
    enabled = False

    async def fetch_cover_url(self, session: aiohttp.ClientSession, url: str):
        page = await self.helpers.scrape_and_cook(session, url)
        return page.select('span.info-image img')[0]['src']

    async def fetch_title(self, session: aiohttp.ClientSession, url: str):
        page = await self.helpers.scrape_and_cook(session, url)
        return page.select('div.story-info-right h1')[0].text

    async def fetch_chapters(self, session: aiohttp.ClientSession, url: str) -> List[Chapter]:
        page = await self.helpers.scrape_and_cook(session, url)

        chapters = []
        for chapter in page.select('a.chapter-name'):
            meta = re.search(r'Vol.(\d*) Chapter (.*): *(.*)', chapter.text)

            volume = meta.group(1) if meta else None
            index = meta.group(2) if meta else ''
            title = meta.group(3) if meta else ''
            url = chapter['href']

            chapters.append(Chapter(
                volume=volume,
                index=index,
                title=title,
                url=url
            ))

        return chapters

    async def fetch_pages(self, session: aiohttp.ClientSession, chapter: Chapter) -> List[Page]:
        page = await self.helpers.scrape_and_cook(session, chapter.url)

        pages = []
        for image in page.select('div.container-chapter-reader img'):
            url = image['src']
            pages.append(Page(
                url=url,
                index=int(re.search(r'.*\/(\d+)\..*', url).group(1))
            ))

        return pages


provider = ManganeloCom
