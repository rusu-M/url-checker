import asyncio
from dataclasses import dataclass
import httpx
import time


@dataclass
class InfoResult:
    url: str
    elapsed: float
    code: int | None
    error: str | None


def read_urls(path: str) -> list:
    with open(path, mode='r', encoding='utf-8') as f:
        urls = [url.strip() for url in f.readlines()]
    return urls


async def url_checker(url, client):
    start = time.perf_counter()
    try:
        response = await client.get(url)
        return InfoResult(url, elapsed=time.perf_counter() - start, code=response.status_code, error=None)
    except httpx.RequestError as e:
        return InfoResult(url, elapsed=time.perf_counter() - start, code=None, error=repr(e))
    


async def main():

    urls = read_urls(path=input("Введите путь: "))


    httpxclient = httpx.AsyncClient()
    start = time.perf_counter()
    async with httpxclient as client:
        results = await asyncio.gather(*(url_checker(u, client) for u in urls))
    end = time.perf_counter() - start
    for r in results:
        print(r)

    print("\n\n\n--------Статистика--------")
    print(f"--------Всего urls {len(results)}")
    print(f"--------Количество дошедших {sum(1 for r in results if r.code is not None)}")
    print(f"--------Падшие {sum(1 for r in results if r.code is None)}")
    print(f"--------Общее время {end}")

if __name__ == "__main__":
    asyncio.run(main())
