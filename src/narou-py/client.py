import enum
import urllib.parse

class ProxyType(enum.Enum):
    Http = enum.auto()
    Https = enum.auto()

class Client:
    BASE = "https://api.syosetu.com"

    def __init__(self, proxies: dict[ProxyType, str] | None = None) -> None:
        if proxies is None:
            return
        self.proxies = dict()
        for proxy_type, url in proxies.items():
            result = urllib.parse.urlparse(url)
            if all([result.scheme, result.netloc]):
                match proxy_type:
                    case ProxyType.Http:
                        self.proxies.update(http=url)
                    case ProxyType.Https:
                        self.proxies.update(https=url)
            else:
                raise ValueError("Please use a valid proxy URL!")