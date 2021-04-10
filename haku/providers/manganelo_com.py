import re
from typing import Dict, List

import aiohttp

from haku.meta import Chapter, Page
from haku.provider import Provider
from haku.raw.endpoints import Endpoints

# TODO(me) switch images server


class ManganeloEndpoints(Endpoints):
    """Manganelo.com endpoints"""

    # TODO(me) find a more elegant way to share states
    _chapters_refs = {}

    def get_headers(self, url: str) -> Dict[str, str]:
        """Get custom headers"""

        if url in self._chapters_refs:
            return {"Referer": self._chapters_refs[url]}

        return {}


class ManganeloCom(Provider):
    """Manganelo.com provider"""

    name = "manganelo.com"
    pattern = r"^https://manganelo.com"
    endpoints = ManganeloEndpoints
    force_fetch = True

    re_chapter_title = (
        r"(?:Vol.(?P<volume>(.*)) )?Chapter (?P<index>[^\n:]*)(?:: *(?P<title>.*))?"
    )

    async def fetch_cover(self, session: aiohttp.ClientSession, url: str):
        page = await self.helpers.scrape_and_cook(session, url)
        return page.select("span.info-image img")[0]["src"]

    async def fetch_title(self, session: aiohttp.ClientSession, url: str):
        page = await self.helpers.scrape_and_cook(session, url)
        return page.select("div.story-info-right h1")[0].text

    async def fetch_chapters(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[Chapter]:
        page = await self.helpers.scrape_and_cook(session, url)

        chapters = []
        for chapter in page.select("a.chapter-name"):
            meta = re.search(self.re_chapter_title, chapter.text)

            index = float(meta.group("index"))
            title = meta.group("title") or ""
            url = chapter["href"]
            volume = meta.group("volume")
            if volume is not None:
                volume = float(volume)

            chapters.append(Chapter(volume=volume, index=index, title=title, url=url))

        return chapters

    async def fetch_pages(
        self, session: aiohttp.ClientSession, chapter: Chapter
    ) -> List[Page]:
        page = await self.helpers.scrape_and_cook(session, chapter.url)

        pages = []
        for image in page.select("div.container-chapter-reader img"):
            url = image["src"]
            pages.append(
                Page(url=url, index=int(re.search(r".*\/(\d+)\..*", url).group(1)))
            )

            self.endpoints._chapters_refs[url] = chapter.url

        return pages


provider = ManganeloCom
