import asyncio
from dataclasses import dataclass
import httpx
import time
import sys


@dataclass
class InfoResult:
    url: str
    elapsed: float
    code: int | None
    error: str | None
    timeout: str | None


def read_urls(path: str) -> list:
    with open(path, mode="r", encoding="utf-8") as f:
        urls = [url.strip() for url in f.readlines()]
    return urls


async def url_checker(url, client, sem):
    async with sem:
        start = time.perf_counter()
        try:
            response = await client.get(url, timeout=4)
            return InfoResult(
                url,
                elapsed=time.perf_counter() - start,
                code=response.status_code,
                error=None,
                timeout=None,
            )
        except httpx.TimeoutException as e:
            return InfoResult(
                url,
                elapsed=time.perf_counter() - start,
                code=None,
                error=None,
                timeout=repr(e),
            )
        except httpx.RequestError as e:
            return InfoResult(
                url,
                elapsed=time.perf_counter() - start,
                code=None,
                error=repr(e),
                timeout=None,
            )


async def main():
    if len(sys.argv) < 2:
        print("Использование: python url_checker.py <путь-к-файлу>")
        sys.exit(1)
    urls = read_urls(path=sys.argv[1])

    semaphore = asyncio.Semaphore(4)
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(url_checker(u, client, semaphore) for u in urls)
        )
    end = time.perf_counter() - start
    for r in results:
        print(r)

    print("\n\n\n--------Статистика--------")
    print(f"--------Всего urls {len(results)}")
    print(
        f"--------Количество дошедших {sum(1 for r in results if r.code is not None)}"
    )
    print(f"--------Падшие {sum(1 for r in results if r.error is not None)}")
    print(f"--------timeout {sum(1 for r in results if r.timeout is not None)}")
    print(f"--------Общее время {end}")


if __name__ == "__main__":
    asyncio.run(main())
