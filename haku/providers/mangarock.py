from haku.provider import Provider, Helpers
from haku.meta import Chapter, Page
from typing import List
import aiohttp
import json
import re


class Mangarock(Provider):
    name = 'mangarock'
    pattern = r'^https://mangarock.to'

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
