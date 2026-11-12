<p align="center">
  <a href="https://fusionproxy.net/?utm_source=github&utm_medium=proxy-anonymity-test">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/FusionProxies/.github/main/assets/logo-on-dark.png">
      <img src="https://raw.githubusercontent.com/FusionProxies/.github/main/assets/logo-on-light.png" alt="Fusion Proxy" height="52">
    </picture>
  </a>
</p>

# Proxy anonymity test: transparent, anonymous and elite proxies

A proxy can hide your IP completely, hide it but announce that it is a proxy, or pass your real IP straight to the website. This repository explains the three anonymity levels, which headers give a proxy away, and includes [`anonymity_check.py`](anonymity_check.py), a script that tests any list of proxies and tells you which level each one really is.

```bash
pip install -r requirements.txt
python anonymity_check.py http://203.0.113.10:8080 socks5h://198.51.100.7:1080
python anonymity_check.py -f proxies.txt
python anonymity_check.py --free 40          # the first 40 HTTP proxies of our free list
```

## The three levels

| Level | Your real IP | Says it is a proxy | Typical headers the website receives |
|---|---|---|---|
| **Transparent** | Visible | Yes | `X-Forwarded-For: <your IP>`, `Via`, `Forwarded: for=<your IP>` |
| **Anonymous** | Hidden | Yes | `Via: 1.1 proxy`, `X-Forwarded-For: <proxy IP>`, `Proxy-Connection` |
| **Elite** (high anonymity) | Hidden | No | Only what a normal browser sends |

Transparent proxies are meant for caching and company networks, not for privacy: the site sees exactly who you are. Anonymous proxies hide you, but sites that dislike proxies block them on sight. Elite proxies look like an ordinary visitor.

## What we found

`--free 40` on a public free proxy list, plus one residential proxy, November 2026:

```
elite        resi.fusionproxy.net:12286         -
elite        http://103.237.102.191:11111       -
transparent  http://144.124.251.24:10689        Forwarded
transparent  http://103.155.199.185:8080        X-Proxy-Id
...
10 elite, 0 anonymous, 12 transparent, 19 dead
```

More than half of the working free proxies were **transparent**: over plain HTTP they told the website the real IP of whoever used them, although the upstream list describes itself as anonymizing proxies. Test before you trust.

## How the test works

1. It finds your real IPv4 and IPv6 address (via `api.ipify.org`).
2. Through each proxy it requests `http://httpbin.org/get`, a "judge" that echoes back the IP it saw and every request header.
3. If your real IP appears anywhere in the answer, the proxy is **transparent**. If not, but any proxy header from the list below is present, it is **anonymous**. Otherwise **elite**.

Headers checked: `Via`, `X-Forwarded-For`, `Forwarded`, `X-Real-Ip`, `X-Proxy-Id`, `Proxy-Connection`, `X-Forwarded-Host`, `X-Forwarded-Proto`, `Client-Ip`, `X-Client-Ip`, `X-Originating-Ip`.

The judge URL is plain `http://` on purpose. On `https://` sites the proxy only opens an encrypted tunnel (`CONNECT`) and cannot add or read headers, so every working proxy looks elite there. Anonymity levels matter for plain HTTP traffic, and for proxies that break HTTPS, which you should not use at all.

## Beyond headers

Headers are only one way a proxy is detected. Websites also check:

- **IP reputation**: datacenter ranges and IPs on public proxy lists are flagged no matter what the headers say. Residential IPs belong to home connections and are rarely on such lists.
- **DNS leaks**: with `socks5://` (not `socks5h://`) or a browser that resolves names locally, your own DNS server sees every site you visit.
- **WebRTC leaks**: a browser can reveal your real IP through WebRTC even behind a proxy. Test it with the [WebRTC leak test](https://fusionproxy.net/tools/webrtc-leak-test?utm_source=github&utm_medium=proxy-anonymity-test).
- **Location mismatches**: an IP in Germany with a browser set to US time zone and language stands out.

## Related

- [proxy-checker](https://github.com/FusionProxies/proxy-checker): speed, exit IP and country for thousands of proxies
- [What is my IP](https://fusionproxy.net/tools/my-ip?utm_source=github&utm_medium=proxy-anonymity-test) and the [online proxy checker](https://fusionproxy.net/tools/proxy-checker?utm_source=github&utm_medium=proxy-anonymity-test)

Need elite proxies with clean IPs? [Fusion Proxy residential proxies](https://fusionproxy.net/proxies/residential?utm_source=github&utm_medium=proxy-anonymity-test) from $2.95/GB, with a [free trial](https://fusionproxy.net/free-trial?utm_source=github&utm_medium=proxy-anonymity-test).

## License

MIT, see [LICENSE](LICENSE).
