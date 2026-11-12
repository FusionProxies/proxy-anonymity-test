"""Check proxy anonymity: transparent, anonymous or elite.

Sends a plain-HTTP request through each proxy to a "judge" that echoes the
request headers back (httpbin.org/get), then looks for your real IP and for
headers that reveal a proxy.

    pip install -r requirements.txt
    python anonymity_check.py http://203.0.113.10:8080 socks5h://198.51.100.7:1080
    python anonymity_check.py -f proxies.txt
    python anonymity_check.py --free 25          # first 25 HTTP proxies of the free list
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor

import requests

JUDGE = "http://httpbin.org/get"  # plain HTTP on purpose: over HTTPS a proxy cannot add headers
FREE_LIST = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"  # public MIT list by monosans

# headers that proxies add, and that give them away
PROXY_HEADERS = ["Via", "X-Forwarded-For", "Forwarded", "X-Real-Ip", "X-Proxy-Id", "Proxy-Connection",
                 "X-Forwarded-Host", "X-Forwarded-Proto", "Client-Ip", "X-Client-Ip", "X-Originating-Ip", "Cache-Control-Proxy"]


def real_ips() -> set[str]:
    ips = set()
    for url in ("https://api.ipify.org", "https://api64.ipify.org"):  # IPv4 and IPv6
        try:
            ips.add(requests.get(url, timeout=15).text.strip())
        except requests.RequestException:
            pass
    return ips


def classify(proxy: str, mine: set[str]) -> dict:
    try:
        r = requests.get(JUDGE, proxies={"http": proxy, "https": proxy}, timeout=15)
        data = r.json()
    except (requests.RequestException, json.JSONDecodeError) as e:
        return {"proxy": proxy, "level": "dead", "detail": type(e).__name__}
    headers = {k.title(): v for k, v in data.get("headers", {}).items()}
    seen = " ".join([data.get("origin", "")] + list(headers.values()))
    revealing = [h for h in PROXY_HEADERS if h.title() in headers]
    if any(ip and ip in seen for ip in mine):
        level = "transparent"   # the site sees your real IP
    elif revealing:
        level = "anonymous"     # your IP is hidden, but the site can tell a proxy is used
    else:
        level = "elite"         # no trace of you or of a proxy
    return {"proxy": proxy, "level": level, "detail": ", ".join(revealing) or "-", "origin": data.get("origin", "")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("proxies", nargs="*")
    ap.add_argument("-f", "--file")
    ap.add_argument("--free", type=int, default=0, help="test the first N proxies of the free HTTP list")
    a = ap.parse_args()
    proxies = list(a.proxies)
    if a.file:
        proxies += open(a.file, encoding="utf-8").read().split()
    if a.free:
        proxies += requests.get(FREE_LIST, timeout=30).text.split()[: a.free]
    proxies = [p if "://" in p else "http://" + p for p in proxies]
    if not proxies:
        ap.error("give proxies as arguments, with -f, or with --free N")

    mine = real_ips()
    print(f"your real IPs: {', '.join(sorted(mine)) or 'unknown'}\n")
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(lambda p: classify(p, mine), proxies))

    for r in results:
        shown = r["proxy"].split("@")[-1]  # never print credentials
        print(f"{r['level']:<12} {shown:<34} {r['detail']}")
    counts = {lvl: sum(r["level"] == lvl for r in results) for lvl in ("elite", "anonymous", "transparent", "dead")}
    print("\n" + ", ".join(f"{n} {lvl}" for lvl, n in counts.items()))


if __name__ == "__main__":
    main()
