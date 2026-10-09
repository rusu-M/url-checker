from dataclasses import dataclass
import time
import sys
import requests
from concurrent.futures import ThreadPoolExecutor

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


def checker(url):
    start = time.perf_counter()
    try:
        answer = requests.get(url, timeout=4)
        return InfoResult(
            url,
            elapsed=time.perf_counter() - start,
            code=answer.status_code,
            error=None,
            timeout=None,
        )
    except requests.exceptions.Timeout as e:
        return InfoResult(
            url,
            elapsed=time.perf_counter() - start,
            code=None,
            error=None,
            timeout=repr(e),
        )
    except requests.exceptions.RequestException as e:
        return InfoResult(
            url,
            elapsed=time.perf_counter() - start,
            code=None,
            error=repr(e),
            timeout=None
        )
    

def main():
    if len(sys.argv) < 2:
        print("Использование: python checker_threads_v.py <путь-к-файлу>")
        sys.exit(1)
    urls = read_urls(sys.argv[1])

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(checker, urls)
    end = time.perf_counter() - start

    for res in results:
        print(res)

    print(f"\n_____Время работы многопоточной версии для {len(urls)} обращений: {end}")

if __name__ == "__main__":
    main()