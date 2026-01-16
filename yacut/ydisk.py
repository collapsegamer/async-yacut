import aiohttp

DISK_API = 'https://cloud-api.yandex.net/v1/disk/resources'
UPLOAD_ENDPOINT = f'{DISK_API}/upload'
DOWNLOAD_ENDPOINT = f'{DISK_API}/download'


class YDiskError(RuntimeError):
    pass


def _headers(token: str) -> dict:
    return {'Authorization': f'OAuth {token}'}


async def get_upload_href(session: aiohttp.ClientSession, token: str,
                          path: str) -> str:
    params = {'path': path, 'overwrite': 'true'}
    async with session.get(UPLOAD_ENDPOINT, headers=_headers(token),
                           params=params) as r:
        data = await r.json(content_type=None)
        if r.status >= 400:
            raise YDiskError(str(data))
        return data['href']


async def upload_bytes(session: aiohttp.ClientSession, href: str,
                       content: bytes) -> None:
    async with session.put(href, data=content) as r:
        if r.status >= 400:
            raise YDiskError(await r.text())


async def get_download_href(session: aiohttp.ClientSession, token: str,
                            path: str) -> str:
    params = {'path': path}
    async with session.get(DOWNLOAD_ENDPOINT, headers=_headers(token),
                           params=params) as r:
        data = await r.json(content_type=None)
        if r.status >= 400:
            raise YDiskError(str(data))
        return data['href']


async def download_bytes(session: aiohttp.ClientSession, href: str) -> bytes:
    async with session.get(href) as r:
        if r.status >= 400:
            raise YDiskError(await r.text())
        return await r.read()
