import json, os, sys, urllib.request
from xml.sax.saxutils import escape as esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'
PAL = {
    "dark":  dict(bg="#0d1117", panel="#161b22", bar="#1c2128", border="#30363d", fg="#e6edf3", muted="#8b949e", acc="#3fb950", tag="#d29922"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", bar="#eaeef2", border="#d0d7de", fg="#1f2328", muted="#59636e", acc="#1a7f37", tag="#9a6700"),
}
DEMO = {"commits": 686, "prs": 24, "merged": 22, "langs": [
    ("TypeScript", 34.5, "#3178c6"), ("JavaScript", 30.2, "#f1e05a"), ("Rust", 15.7, "#dea584"), ("Python", 9.7, "#3572A5"),
    ("C++", 2.6, "#f34b7d"), ("Shell", 2.4, "#89e051"), ("PHP", 1.7, "#4F5D95"), ("Go", 1.7, "#00ADD8")]}


def gql(token, query, **variables):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 json.dumps({"query": query, "variables": variables}).encode(),
                                 {"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if d.get("errors") or not d.get("data"):
        raise RuntimeError("GraphQL error")
    return d["data"]


def fetch(token, login):
    u = gql(token, "query($l:String!){user(login:$l){pullRequests{totalCount} merged:pullRequests(states:MERGED){totalCount}"
                   " contributionsCollection{contributionYears}}}", l=login)["user"]
    total = restricted = 0
    for y in u["contributionsCollection"]["contributionYears"]:
        c = gql(token, "query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t)"
                       "{totalCommitContributions restrictedContributionsCount}}}",
                l=login, f=f"{y}-01-01T00:00:00Z", t=f"{y}-12-31T23:59:59Z")["user"]["contributionsCollection"]
        total += c["totalCommitContributions"]
        restricted += c["restrictedContributionsCount"]
    langs, cursor = {}, None
    while True:
        r = gql(token, "query($l:String!,$a:String){user(login:$l){repositories(first:100,ownerAffiliations:OWNER,isFork:false,after:$a)"
                       "{pageInfo{hasNextPage endCursor} nodes{languages(first:20,orderBy:{field:SIZE,direction:DESC})"
                       "{edges{size node{name color}}}}}}}", l=login, a=cursor)["user"]["repositories"]
        for n in r["nodes"]:
            for e in n["languages"]["edges"]:
                v = langs.setdefault(e["node"]["name"], [0, e["node"]["color"]])
                v[0] += e["size"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        cursor = r["pageInfo"]["endCursor"]
    top = sorted(((k, v[0], v[1]) for k, v in langs.items() if k not in ("HTML", "CSS")), key=lambda x: -x[1])[:8]
    s = sum(b for _, b, _ in top) or 1
    return {"commits": total or restricted, "prs": u["pullRequests"]["totalCount"], "merged": u["merged"]["totalCount"],
            "langs": [(n, round(b * 100 / s, 1), c) for n, b, c in top]}


def num(n):
    return f"{n / 1000:.1f}k" if n >= 10000 else str(n)


def T(x, y, s, size, fill, weight="normal"):
    return f'<text x="{x}" y="{y}" font-family=\'{MONO}\' font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(s)}</text>'


def render(data, p):
    W, H = 1200, 230
    b = ""
    for i, (label, key) in enumerate((("COMMITS", "commits"), ("PULL REQUESTS", "prs"), ("MERGED", "merged"))):
        x, s = 32 + i * 128, num(data[key])
        size = min(44, int(112 / (0.65 * len(s))))
        b += T(x, 118, s, size, p["fg"], "bold") + T(x, 148, label, 12, p["acc"], "bold")
    b += f'<line x1="424.5" y1="40" x2="424.5" y2="190" stroke="{p["border"]}"/>'
    X0, BW = 456, 712
    b += T(X0, 66, "LANGUAGES", 13, p["acc"], "bold")
    langs = data["langs"]
    tot = sum(pc for _, pc, _ in langs) or 1
    x, segs = X0, ""
    for _, pc, col in langs:
        w = BW * pc / tot
        segs += f'<rect x="{x:.2f}" y="84" width="{w:.2f}" height="12" fill="{col or p["muted"]}"/>'
        x += w
    b += f'<clipPath id="b"><rect x="{X0}" y="84" width="{BW}" height="12" rx="6"/></clipPath><g clip-path="url(#b)">{segs}</g>'
    for i, (name, pc, col) in enumerate(langs[:8]):
        lx, ly = X0 + (i % 4) * 178, 140 + (i // 4) * 36
        nm = name if len(name) <= 10 else name[:9] + "…"
        b += f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{col or p["muted"]}"/>'
        b += T(lx + 16, ly, nm, 14, p["fg"]) + T(lx + 16 + len(nm) * 8.8 + 10, ly, f"{pc:.1f}%", 13, p["muted"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{p["panel"]}" stroke="{p["border"]}" stroke-width="1"/>'
            + b + '</svg>')


def main():
    if "--demo" in sys.argv:
        data = DEMO
    else:
        token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("No STATS_TOKEN or GITHUB_TOKEN set")
        try:
            data = fetch(token, os.environ.get("GH_LOGIN", "Fem10da"))
        except Exception as e:
            sys.exit(f"Stats fetch failed: {type(e).__name__} {getattr(e, 'code', '')}")
    os.makedirs(os.path.join(ROOT, "stats"), exist_ok=True)
    for th, p in PAL.items():
        with open(os.path.join(ROOT, "stats", f"activity-{th}.svg"), "w", encoding="utf-8") as f:
            f.write(render(data, p))


if __name__ == "__main__":
    main()
