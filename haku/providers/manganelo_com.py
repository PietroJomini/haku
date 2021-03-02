from haku.provider import Provider


class ManganeloCom(Provider):
    """Manganelo.com provider"""

    name = 'manganelo.com'
    pattern = r'^https://mangarock.to'

    async def fetch_cover_url(self, session: aiohttp.ClientSession, url: str):
        page = await self.helpers.scrape_and_cook(session, url)
        thumb = page.select('div.thumb div')[0]['style']
        meta = re.search(r'background-image: url\(\'(.*)\'\);', thumb)
        return meta.group(1)

    async def fetch_title(self, session: aiohttp.ClientSession, url: str):
        page = await self.helpers.scrape_and_cook(session, url)
        return page.select('div.info h1')[0].text

    async def fetch_chapters(self, session: aiohttp.ClientSession, url: str) -> List[Chapter]:
        page = await self.helpers.scrape_and_cook(session, url)

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

    async def fetch_pages(self, session: aiohttp.ClientSession, chapter: Chapter) -> List[Page]:
        page = await self.helpers.scrape_and_cook(session, chapter.url)

        pages = []
        meta = re.search(r'var mangaData = (.*?);', str(page))
        for index, page in enumerate(json.loads(meta.group(1))):
            pages.append(Page(
                url=page['url'],
                index=index
            ))

        return pages


provider = ManganeloCom
