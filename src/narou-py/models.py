from __future__ import annotations
import dataclasses
import typing
import urllib.parse
import gzip
import io
import json
import collections.abc
import datetime

import httpx
import defusedxml.ElementTree

import client


@dataclasses.dataclass
class User:
    name: str
    userid: int
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
                userid,
                data["yomikata"],
                data["novel_cnt"],
                data["review_cnt"],
                data["novel_length"],
                data["sum_global_point"],
            )

    async def get_blog(
        self, proxies: dict[client.ProxyType, str] | None = None
    ) -> Blog:
        return await Blog.new(self.userid, proxies)


@dataclasses.dataclass
class Blog:
    author: User
    title: str
    subtitle: str
    entries: collections.abc.Sequence[BlogEntry]

    @classmethod
    async def new(
        cls, user: int | User, proxies: dict[client.ProxyType, str] | None = None
    ) -> typing.Self:
        async with httpx.AsyncClient(proxy=proxies) as c:
            if isinstance(user, int):
                response = await c.get(
                    f"https://api.syosetu.com/writerblog/{user}.Atom"
                )
                user = await User.new(user, proxies)
            else:
                response = await c.get(
                    f"https://api.syosetu.com/writerblog/{user.userid}.Atom"
                )
            content = defusedxml.ElementTree.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = list()
            for entry in content.findall("atom:entry", ns):
                entries.append(
                    BlogEntry(
                        entry.find("atom:title", ns).text,
                        entry.find("atom:summary", ns).text,
                        datetime.datetime.fromisoformat(
                            entry.find("atom:published", ns).text
                        ),
                        datetime.datetime.fromisoformat(
                            entry.find("atom:updated", ns).text
                        ),
                        urllib.parse.urlparse(
                            entry.find("atom:id", ns).text
                        ).path.split("/")[-1],
                    )
                )
            return cls(
                user,
                content.find("atom:title", ns).text,
                content.find("atom:subtitle", ns).text,
                entries,
            )


@dataclasses.dataclass
class BlogEntry:
    title: str
    summary: str
    published: datetime.datetime
    updated: datetime.datetime
    entryid: int
