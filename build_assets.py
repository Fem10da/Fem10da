import os
from xml.sax.saxutils import escape as esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
STATS = os.path.join(os.path.dirname(OUT), "stats")
PAL = {
    "dark":  dict(bg="#0d1117", panel="#161b22", bar="#1c2128", border="#30363d", fg="#e6edf3", muted="#8b949e", acc="#3fb950", tag="#d29922"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", bar="#eaeef2", border="#d0d7de", fg="#1f2328", muted="#59636e", acc="#1a7f37", tag="#9a6700"),
}

CARDS = {
    "glpi": ("glpi-helpdesk-bot", "production", "Telegram bot in front of a GLPI helpdesk. Users write naturally, the bot structures the request and creates the right ticket.", ["Node.js", "Telegraf", "GLPI API", "SQLite"]),
    "kg": ("knowledge-graph-mcp", "solo pilot", "Corporate knowledge base exposed to AI assistants through an MCP server, with vector search over embeddings.", ["MCP", "Supabase", "embeddings"]),
    "autoposting": ("autoposting", "MVP", "Multi-tenant short-video autoposting to YouTube Shorts, Instagram Reels and TikTok, driven from Telegram.", ["n8n", "Postiz", "Telegram"]),
    "bunker": ("bunker-game", "beta", 'My take on the "Bunker" party game: a Telegram Mini App with a shared public screen.', ["TypeScript", "React", "Fastify", "Workers", "PostgreSQL"]),
}
STACK = [
    ("AI", ["LLM APIs (Claude, OpenAI, Gemini)", "RAG", "embeddings", "vector search", "knowledge graphs (Neo4j)", "MCP servers", "AI agents", "voice agents", "local LLMs", "prompt-injection testing", "n8n"]),
    ("Languages", ["TypeScript", "JavaScript", "Python", "Go", "Rust", "PHP", "C"]),
    ("Backend & web", ["Node.js", "Fastify", "REST APIs", "React", "Vue", "Vite", "Cloudflare Workers", "Telegram bots & Mini Apps", "Discord bots"]),
    ("Data", ["PostgreSQL", "Neo4j", "Supabase (pgvector)", "MySQL", "SQLite", "MongoDB"]),
    ("Infrastructure", ["Linux/Debian", "Docker Compose", "nginx", "PM2", "MikroTik/RouterOS", "WireGuard", "DNS/DoH", "firewalling", "Active Directory", "Exchange", "GLPI"]),
]

def wrap(s, n):
    lines, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]

def T(x, y, s, size, fill, fam=MONO, weight="normal", anchor="start"):
    return f'<text x="{x}" y="{y}" font-family=\'{fam}\' font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>'

def svg(w, h, p, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{p["panel"]}" stroke="{p["border"]}" stroke-width="1"/>'
            + body + '</svg>')

def pill(x, y, w, h, text, size, p, color, stroke=None):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="none" stroke="{stroke or p["border"]}" stroke-width="1"/>'
            + T(x + w / 2, y + h / 2 + size * 0.35, text, size, color, anchor="middle"))

def banner(p):
    W, H = 1200, 280
    b = f'<clipPath id="c"><rect x="0" y="0" width="{W}" height="{H}" rx="12"/></clipPath>'
    b += f'<g clip-path="url(#c)"><rect x="0" y="0" width="{W}" height="36" fill="{p["bar"]}"/></g>'
    b += f'<line x1="0" y1="36.5" x2="{W}" y2="36.5" stroke="{p["border"]}"/>'
    for i in range(3):
        b += f'<circle cx="{24+i*20}" cy="18" r="5.5" fill="{p["border"]}"/>'
    b += T(W / 2, 23, "~/femida", 13, p["muted"], anchor="middle")
    b += T(40, 84, "$", 22, p["acc"], weight="bold") + T(62, 84, "whoami", 22, p["muted"])
    b += T(40, 168, "Femida", 72, p["fg"], weight="bold")
    b += f'<rect x="{40+6*43.5+10:.0f}" y="118" width="30" height="58" fill="{p["acc"]}"/>'
    b += T(40, 212, "Vadim · Head of AI · Kyiv", 24, p["acc"])
    b += T(40, 250, "AI × infrastructure — helpdesk bots, automation pipelines, knowledge graphs", 20, p["muted"], fam=SANS)
    return svg(W, H, p, b)

def card(key, p):
    name, tag, text, chips = CARDS[key]
    W, H = 590, 210
    tw = len(tag) * 7.2 + 24
    b = T(24, 42, name, 22, p["acc"], weight="bold")
    b += pill(W - 24 - tw, 22, tw, 24, tag, 12, p, p["tag"], stroke=p["tag"])
    for i, l in enumerate(wrap(text, 62)[:3]):
        b += T(24, 82 + i * 22, l, 15, p["fg"], fam=SANS)
    x = 24
    for c in chips:
        cw = len(c) * 8 + 22
        assert x + cw <= W - 24, (key, c)
        b += pill(x, 166, cw, 26, c, 12, p, p["muted"])
        x += cw + 8
    return svg(W, H, p, b)

def stack(p):
    W, X0, XL, R = 1200, 32, 222, 1168
    y, b = 20, ""
    for i, (label, items) in enumerate(STACK):
        x, line, chips = XL, 0, ""
        for it in items:
            cw = len(it) * 8.6 + 26
            if x + cw > R:
                x, line = XL, line + 1
            chips += pill(round(x), y + line * 40, round(cw), 30, it, 14, p, p["fg"])
            x += cw + 8
        b += T(X0, y + 20, label.upper(), 13, p["acc"], weight="bold")
        y += (line + 1) * 40 - 10 + 20
        if i < len(STACK) - 1:
            b += f'<line x1="{X0}" y1="{y-10}" x2="{W-X0}" y2="{y-10}" stroke="{p["border"]}"/>'
        b += chips
    return svg(W, y, p, b)

def placeholder(w, title, p):
    return svg(w, 195, p, T(25, 38, title, 18, p["acc"], weight="bold") + T(25, 70, "updates after the first workflow run", 13, p["muted"]))

def main():
    os.makedirs(STATS, exist_ok=True)
    for th, p in PAL.items():
        for n, w, t in (("stats", 467, "Activity"), ("langs", 300, "Languages")):
            with open(os.path.join(STATS, f"{n}-{th}.svg"), "w", encoding="utf-8") as f:
                f.write(placeholder(w, t, p))
    for th, p in PAL.items():
        files = {"banner": banner(p)}
        files.update({f"card-{k}": card(k, p) for k in CARDS})
        files["stack"] = stack(p)
        for n, s in files.items():
            with open(os.path.join(OUT, f"{n}-{th}.svg"), "w", encoding="utf-8") as f:
                f.write(s)

main()
