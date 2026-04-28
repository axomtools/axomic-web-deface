

import os
import re
import json
import time
import urllib.request
import urllib.parse
import ssl
import gzip
import subprocess
from datetime import datetime
from urllib.parse import urlparse, urljoin

colors = {
    'red': '\033[0;31m',
    'green': '\033[0;32m',
    'yellow': '\033[1;33m',
    'blue': '\033[0;34m',
    'purple': '\033[0;35m',
    'cyan': '\033[0;36m',
    'white': '\033[1;37m',
    'nc': '\033[0m'
}

if len(os.sys.argv) < 2:
    print(f"{colors['red']}┌────────────────────────────────────────┐{colors['nc']}")
    print(f"{colors['red']}│{colors['white']}  axomicwebdeface - website extractor     {colors['red']}│{colors['nc']}")
    print(f"{colors['red']}├────────────────────────────────────────┤{colors['nc']}")
    print(f"{colors['red']}│{colors['yellow']}  usage: python axomicwebdeface <url>      {colors['red']}│{colors['nc']}")
    print(f"{colors['red']}│{colors['yellow']}  example: python axomicwebdeface https://x.com{colors['red']}│{colors['nc']}")
    print(f"{colors['red']}└────────────────────────────────────────┘{colors['nc']}")
    os.sys.exit(1)

ssl._create_default_https_context = ssl._create_unverified_context

starturl = os.sys.argv[1]
parsed = urlparse(starturl)
basehost = parsed.netloc
schemeprefix = f"{parsed.scheme}://{basehost}"
websitename = re.sub(r'^www\.', '', basehost)
websitename = re.sub(r'\..*$', '', websitename)

savedir = '/sdcard/Download/axomic-website-deface'
outputdir = f"{savedir}/{websitename}"

dirs = [
    outputdir, f"{outputdir}/html", f"{outputdir}/js", f"{outputdir}/css",
    f"{outputdir}/assets/images", f"{outputdir}/assets/videos", f"{outputdir}/assets/audio",
    f"{outputdir}/assets/documents", f"{outputdir}/assets/fonts", f"{outputdir}/scans",
    f"{outputdir}/network", f"{outputdir}/database", f"{outputdir}/auth", f"{outputdir}/storage",
    f"{outputdir}/server", f"{outputdir}/dynamic", f"{outputdir}/api",
    f"{outputdir}/client", f"{outputdir}/logs"
]

for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)

os.system('clear')
print(f"{colors['cyan']}╔════════════════════════════════════════════════════════════════╗{colors['nc']}")
print(f"{colors['cyan']}║{colors['white']}                      AXOMIC WEBSITE DEFACE TOOL                      {colors['cyan']}║{colors['nc']}")
print(f"{colors['cyan']}╚════════════════════════════════════════════════════════════════╝{colors['nc']}")
print('')
print(f"{colors['green']}▸{colors['white']} target    : {colors['yellow']}{starturl}{colors['nc']}")
print(f"{colors['green']}▸{colors['white']} name      : {colors['yellow']}{websitename}{colors['nc']}")
print(f"{colors['green']}▸{colors['white']} output    : {colors['yellow']}{outputdir}{colors['nc']}")
print('')

print(f"{colors['purple']}░{colors['white']} fetching main page and discovering resources...{colors['nc']}")

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def fetchurl(target):
    try:
        req = urllib.request.Request(target, headers=headers)
        resp = urllib.request.urlopen(req, timeout=20)
        data = resp.read()
        if resp.info().get('Content-Encoding') == 'gzip':
            data = gzip.decompress(data)
        return data, resp
    except:
        return None, None

def fetchtext(target):
    data, _ = fetchurl(target)
    if data:
        return data.decode('utf-8', errors='ignore')
    return None

def extracturls(content, base):
    urls = set()
    patterns = [
        r'href=["\']([^"\']+)["\']',
        r'src=["\']([^"\']+)["\']',
        r'action=["\']([^"\']+)["\']',
        r'data-url=["\']([^"\']+)["\']',
        r'data-src=["\']([^"\']+)["\']'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content, re.I)
        for match in matches:
            if match.startswith('http'):
                urls.add(match)
            elif match.startswith('/'):
                urls.add(urljoin(base, match))
            elif match and not match.startswith('#') and not match.startswith('mailto:') and not match.startswith('javascript:'):
                urls.add(urljoin(base, match))
    return urls

mainhtml = fetchtext(starturl)
if not mainhtml:
    print(f"{colors['red']}  ✗ failed to fetch {starturl}{colors['nc']}")
    exit(1)

with open(f"{outputdir}/html/index.html", 'w', encoding='utf-8') as f:
    f.write(mainhtml)

baseurl = starturl
allhtml = set([starturl])
alljs = set()
allcss = set()
allassets = set()
allapi = set()

newurls = extracturls(mainhtml, starturl)
for u in newurls:
    if basehost in u:
        if re.search(r'\.(html|htm|php|asp|aspx|jsp)$', u, re.I) or '/' in u and not re.search(r'\.(js|css|png|jpg|jpeg|gif|svg|webp|ico|mp4|mp3|pdf|zip|woff|ttf)$', u, re.I):
            allhtml.add(u)
        elif re.search(r'\.(js|mjs|cjs|ts|tsx|jsx)$', u, re.I):
            alljs.add(u)
        elif re.search(r'\.(css|scss|sass|less)$', u, re.I):
            allcss.add(u)
        elif re.search(r'\.(png|jpg|jpeg|gif|svg|webp|ico|mp4|mp3|wav|ogg|pdf|zip|doc|docx|xls|xlsx|woff|woff2|ttf)$', u, re.I):
            allassets.add(u)
        elif '/api/' in u or '/v1/' in u or '/v2/' in u or '/graphql' in u or '/rest/' in u:
            allapi.add(u.split('?')[0])

print(f"{colors['green']}  ✔{colors['white']} found {len(allhtml)} html, {len(alljs)} js, {len(allcss)} css, {len(allapi)} api{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} downloading all html pages...{colors['nc']}")

htmlcontent = {}
for i, htmlurl in enumerate(list(allhtml)[:50]):
    content = fetchtext(htmlurl)
    if content:
        safename = re.sub(r'[^a-zA-Z0-9]', '_', htmlurl.replace(starturl, ''))[:40]
        if not safename:
            safename = f"page{i}"
        savepath = f"{outputdir}/html/{safename}.html"
        with open(savepath, 'w', encoding='utf-8') as f:
            f.write(content)
        htmlcontent[htmlurl] = content

print(f"{colors['green']}  ✔{colors['white']} downloaded {len(htmlcontent)} html pages{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} downloading all javascript files...{colors['nc']}")

jscontent = {}
for jsurl in list(alljs)[:100]:
    content = fetchtext(jsurl)
    if content:
        safename = re.sub(r'[^a-zA-Z0-9]', '_', jsurl.split('/')[-1].split('?')[0])[:40]
        if not safename:
            safename = f"script_{len(jscontent)}"
        savepath = f"{outputdir}/js/{safename}.js"
        with open(savepath, 'w', encoding='utf-8') as f:
            f.write(content)
        jscontent[jsurl] = content

print(f"{colors['green']}  ✔{colors['white']} downloaded {len(jscontent)} javascript files{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} downloading all css files...{colors['nc']}")

csscontent = {}
for cssurl in list(allcss)[:80]:
    content = fetchtext(cssurl)
    if content:
        safename = re.sub(r'[^a-zA-Z0-9]', '_', cssurl.split('/')[-1].split('?')[0])[:40]
        if not safename:
            safename = f"style_{len(csscontent)}"
        savepath = f"{outputdir}/css/{safename}.css"
        with open(savepath, 'w', encoding='utf-8') as f:
            f.write(content)
        csscontent[cssurl] = content

print(f"{colors['green']}  ✔{colors['white']} downloaded {len(csscontent)} css files{colors['nc']}")

allhtmlmerged = "\n\n".join(htmlcontent.values())
alljsmerged = "\n\n".join(jscontent.values())
allcssmerged = "\n\n".join(csscontent.values())

with open(f"{outputdir}/scans/all_html_combined.txt", 'w', encoding='utf-8') as f:
    f.write(allhtmlmerged[:500000])

with open(f"{outputdir}/scans/all_js_combined.js", 'w', encoding='utf-8') as f:
    f.write(alljsmerged)

print(f"{colors['green']}  ✔{colors['white']} merged all files for analysis{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} extracting functions from javascript...{colors['nc']}")

funcs = re.findall(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(([^)]*)\)\s*{', alljsmerged)
funcs += re.findall(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>', alljsmerged)
funcs += re.findall(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\s*\(([^)]*)\)', alljsmerged)

uniquefuncs = list(set([f[0] for f in funcs]))
with open(f"{outputdir}/dynamic/all_functions.txt", 'w') as f:
    f.write(f"total functions: {len(uniquefuncs)}\n\n")
    for fn in sorted(uniquefuncs)[:500]:
        f.write(f"{fn}\n")

with open(f"{outputdir}/dynamic/function_details.txt", 'w') as f:
    f.write("function(params)\n")
    f.write("="*60 + "\n")
    for fname, params in list(set(funcs))[:200]:
        f.write(f"{fname}({params})\n")

print(f"{colors['green']}  ✔{colors['white']} found {len(uniquefuncs)} unique functions{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} analyzing authentication and security...{colors['nc']}")

authfuncs = []
for fname, params in funcs:
    if re.search(r'(login|signin|auth|authenticate|verify|validate|token|session|logout|register|signup|reset|forgot)', fname, re.I):
        authfuncs.append((fname, params))

with open(f"{outputdir}/auth/auth_functions.txt", 'w') as f:
    f.write(f"auth functions found: {len(authfuncs)}\n\n")
    for fname, params in authfuncs[:50]:
        f.write(f"{fname}({params})\n")

allhtmlscan = allhtmlmerged + alljsmerged
forms = re.findall(r'<form[^>]*>.*?</form>', allhtmlscan, re.I | re.DOTALL)
loginforms = [f for f in forms if re.search(r'password|login|signin', f, re.I)]
with open(f"{outputdir}/auth/login_forms.txt", 'w', encoding='utf-8') as f:
    for i, form in enumerate(loginforms[:30]):
        f.write(f"form {i+1}:\n{form[:1000]}\n\n")

tokens = re.findall(r'(?:token|apikey|api_key|secret|password|credential)\s*[:=]\s*["\']([^"\']{8,})["\']', alljsmerged, re.I)
jwt = re.findall(r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}', alljsmerged)
with open(f"{outputdir}/auth/exposed_secrets.txt", 'w') as f:
    f.write(f"secrets found: {len(tokens)}\n")
    for t in tokens[:20]:
        f.write(f"  {t}\n")
    f.write(f"\njwt tokens: {len(jwt)}\n")
    for j in jwt[:10]:
        f.write(f"  {j[:100]}\n")

print(f"{colors['green']}  ✔{colors['white']} found {len(authfuncs)} auth funcs, {len(loginforms)} forms, {len(tokens)} secrets{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} analyzing network requests (incoming + outgoing)...{colors['nc']}")

outgoing = []
outgoing += re.findall(r'fetch\(["\']([^"\']+)["\']', alljsmerged)
outgoing += re.findall(r'\.get\(["\']([^"\']+)["\']', alljsmerged, re.I)
outgoing += re.findall(r'\.post\(["\']([^"\']+)["\']', alljsmerged, re.I)
outgoing += re.findall(r'\.ajax\(\{[^}]*url:\s*["\']([^"\']+)["\']', alljsmerged, re.I)
outgoing += re.findall(r'axios\.(get|post|put|delete)\(["\']([^"\']+)["\']', alljsmerged, re.I)
outgoing = [r[1] if isinstance(r, tuple) else r for r in outgoing]
outgoing = [o for o in outgoing if not o.startswith('http') or basehost in o]

with open(f"{outputdir}/network/outgoing_requests.txt", 'w') as f:
    f.write(f"outgoing requests: {len(set(outgoing))}\n\n")
    for req in sorted(list(set(outgoing)))[:100]:
        f.write(f"{req}\n")

incoming = list(set(allapi))
for u in allhtml:
    if '/api/' in u or '/v1/' in u or '/v2/' in u or '/graphql' in u:
        incoming.append(u.split('?')[0])

incoming = list(set(incoming))
with open(f"{outputdir}/network/incoming_endpoints.txt", 'w') as f:
    f.write(f"incoming api endpoints: {len(incoming)}\n\n")
    for api in sorted(incoming)[:100]:
        f.write(f"{api}\n")

ws = re.findall(r'new\s+WebSocket\(["\']([^"\']+)["\']', alljsmerged)
with open(f"{outputdir}/network/websockets.txt", 'w') as f:
    f.write(f"websockets: {len(set(ws))}\n")
    for w in list(set(ws))[:20]:
        f.write(f"{w}\n")

headersfound = re.findall(r'headers:\s*\{([^}]+)\}', alljsmerged, re.I | re.DOTALL)
with open(f"{outputdir}/network/headers_found.txt", 'w') as f:
    for h in headersfound[:20]:
        f.write(f"{h}\n\n")

alldomains = re.findall(r'https?://([a-zA-Z0-9.-]+)', alljsmerged + allhtmlmerged)
externaldomains = [d for d in set(alldomains) if basehost not in d]
with open(f"{outputdir}/network/external_domains.txt", 'w') as f:
    f.write(f"external domains contacted: {len(externaldomains)}\n")
    for d in sorted(externaldomains)[:50]:
        f.write(f"  {d}\n")

print(f"{colors['green']}  ✔{colors['white']} network: {len(set(outgoing))} outgoing, {len(incoming)} incoming, {len(set(ws))} ws, {len(externaldomains)} external{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} analyzing storage operations...{colors['nc']}")

ls = re.findall(r'localStorage\.(getItem|setItem|removeItem)\(["\']([^"\']*)["\']', alljsmerged)
ss = re.findall(r'sessionStorage\.(getItem|setItem|removeItem)\(["\']([^"\']*)["\']', alljsmerged)
cookies = re.findall(r'document\.cookie\s*=', alljsmerged)
with open(f"{outputdir}/storage/localstorage.txt", 'w') as f:
    f.write(f"operations: {len(ls)}\n")
    for op, key in ls[:30]:
        f.write(f"  {op}('{key}')\n")
with open(f"{outputdir}/storage/sessionstorage.txt", 'w') as f:
    f.write(f"operations: {len(ss)}\n")
    for op, key in ss[:30]:
        f.write(f"  {op}('{key}')\n")
with open(f"{outputdir}/storage/cookies.txt", 'w') as f:
    f.write(f"cookie writes: {len(cookies)}\n")

print(f"{colors['green']}  ✔{colors['white']} storage: {len(ls)} ls, {len(ss)} ss, {len(cookies)} cookie ops{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} analyzing database patterns...{colors['nc']}")

sql = re.findall(r'(?:select|insert|update|delete|create|alter|drop)\s+[\w\s,()]+?(?:from|into|set|where|table)', alljsmerged, re.I)
orm = re.findall(r'\.(?:find|where|select|save|create|update|delete|query|execute|findone)\(', alljsmerged, re.I)
with open(f"{outputdir}/database/sql_patterns.txt", 'w') as f:
    f.write(f"sql-like: {len(sql)}\n")
    for s in sql[:30]:
        f.write(f"  {s[:120]}\n")
    f.write(f"\norm methods: {len(set(orm))}\n")
    for o in list(set(orm))[:30]:
        f.write(f"  {o}\n")

print(f"{colors['green']}  ✔{colors['white']} database: {len(sql)} sql, {len(set(orm))} orm{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} analyzing thirdparty integrations...{colors['nc']}")

third = re.findall(r'(?:googleapis|cloudflare|facebook|twitter|github|stripe|paypal|analytics|gtag|mixpanel|hotjar|segment|sentry|rollbar|newrelic|datadog|amplitude|intercom|zendesk|hubspot)', alljsmerged, re.I)
thirdurls = re.findall(r'https?://(?:[a-z0-9-]+\.)?(?:googleapis|cloudflare|facebook|twitter|github|stripe|paypal|analytics|hotjar|mixpanel|segment|sentry)\.com/[^"\'\s<>]+', alljsmerged, re.I)
with open(f"{outputdir}/dynamic/thirdparty.txt", 'w') as f:
    f.write(f"patterns: {len(set(third))}\n")
    for t in list(set(third))[:30]:
        f.write(f"  {t}\n")
    f.write(f"\nurls: {len(set(thirdurls))}\n")
    for tu in list(set(thirdurls))[:30]:
        f.write(f"  {tu}\n")

print(f"{colors['green']}  ✔{colors['white']} thirdparty: {len(set(third))} services{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} analyzing client capabilities...{colors['nc']}")

webrtc = len(re.findall(r'(?:RTCPeerConnection|getUserMedia|mediaDevices)', alljsmerged, re.I))
webgl = len(re.findall(r'(?:getContext.*webgl|WebGLRenderingContext)', alljsmerged, re.I))
canvas = len(re.findall(r'getContext.*2d|toDataURL', alljsmerged, re.I))
pwa = len(re.findall(r'(?:serviceWorker|manifest\.json|workbox)', alljsmerged, re.I))
with open(f"{outputdir}/client/capabilities.txt", 'w') as f:
    f.write(f"webrtc: {webrtc}\nwebgl: {webgl}\ncanvas: {canvas}\npwa: {pwa}\n")

print(f"{colors['green']}  ✔{colors['white']} client: webrtc={webrtc>0}, webgl={webgl>0}, pwa={pwa>0}{colors['nc']}")

print(f"{colors['purple']}░{colors['white']} generating final report...{colors['nc']}")

report = f"""axomic website deface - complete report
target: {starturl}
website: {websitename}
date: {datetime.now().isoformat()}

extraction summary
──────────────────
html pages: {len(htmlcontent)}
javascript files: {len(jscontent)}
css files: {len(csscontent)}

code analysis
─────────────
functions found: {len(uniquefuncs)}
auth functions: {len(authfuncs)}
login forms: {len(loginforms)}
exposed secrets: {len(tokens)}
jwt tokens: {len(jwt)}

network
───────
outgoing requests: {len(set(outgoing))}
incoming endpoints: {len(incoming)}
websockets: {len(set(ws))}
external domains: {len(externaldomains)}

storage
───────
localstorage ops: {len(ls)}
sessionstorage ops: {len(ss)}
cookie operations: {len(cookies)}

database
────────
sql patterns: {len(sql)}
orm methods: {len(set(orm))}

thirdparty
──────────
services detected: {len(set(third))}
external urls: {len(set(thirdurls))}

client
──────
webrtc: {webrtc>0}
webgl: {webgl>0}
pwa: {pwa>0}

output: {outputdir}"""

with open(f"{outputdir}/scans/complete_report.txt", 'w') as f:
    f.write(report)

print(f"{colors['green']}  ✔{colors['white']} report saved{colors['nc']}")

print('')
print(f"{colors['green']}╔════════════════════════════════════════════════════════════════╗{colors['nc']}")
print(f"{colors['green']}║{colors['white']}                     EXTRACTION COMPLETE                        {colors['green']}║{colors['nc']}")
print(f"{colors['green']}╚════════════════════════════════════════════════════════════════╝{colors['nc']}")
print('')
print(f"{colors['yellow']}▸{colors['white']} output     : {colors['cyan']}{outputdir}{colors['nc']}")
print(f"{colors['yellow']}▸{colors['white']} report     : {colors['cyan']}{outputdir}/scans/complete_report.txt{colors['nc']}")
print('')
