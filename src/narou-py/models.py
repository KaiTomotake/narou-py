import dataclasses
import typing
import urllib.parse
import gzip
import io
import json

import httpx

import client


@dataclasses.dataclass
class User:
    name: str
    read: str
    novel_cnt: int
    review_cnt: int
    novel_length: int
    sum_global_point: int

    @classmethod
    async def new(
        cls, userid: int, proxies: dict[client.ProxyType, str] | None = None
    ) -> typing.Self:
        async with httpx.AsyncClient(proxy=proxies) as c:
            params = {
                "gzip": 5,
                "out": "json",
                "of": "n-y-nc-rc-nl-sg",
                "userid": userid,
            }
            response = await c.get(
                "https://api.syosetu.com/userapi/api?{}".format(
                    urllib.parse.urlencode(params)
                )
            )
            text = gzip.GzipFile(fileobj=io.BytesIO(response.content)).read().decode()
            data = json.loads(text)[1]
            return cls(
                data["name"],
                data["yomikata"],
                data["novel_cnt"],
                data["review_cnt"],
                data["novel_length"],
                data["sum_global_point"],
            )
