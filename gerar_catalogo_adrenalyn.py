# -*- coding: utf-8 -*-
"""
Gera um catalogo HTML autossuficiente das cards Panini FIFA Club World Cup 2025
Adrenalyn XL (387 cards). Mesmas opcoes do catalogo de perfumes: busca, alternar
Cards/Lista, categorias retrateis, carrinho com localStorage e fechamento de
pedido no WhatsApp. Fotos externas em img/<n>.webp (lazy-load).

Rodar:  python gerar_catalogo_cards.py
"""
import os, json, html

# ---------------- CONFIG (editavel) ----------------
MARCA      = "Alvaro Nayder"
SUBTITULO  = "Cards avulsas Panini World Cup 2026 — Adrenalyn XL"
REFERENCIA = "Coleção Adrenalyn XL 2026"
ATUALIZADO = "22/07/2026"
PRECO_UNIT = 1.00                      # preco por carta (por enquanto R$ 1)
CARD_MAX   = 630                       # mostra apenas cards ate este numero (None = todos)
WHATSAPP   = "5537991716781"           # so numeros, 55 + DDD + numero
WHATSAPP_F = "(37) 99171-6781"
INSTAGRAM  = "seu_instagram"           # placeholder
ENDERECO   = "Rua Tupis 174 - Moema"

ARQ_DADOS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards_data.json")
SAIDA      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogo.html")
IMG_DIR    = "img"                     # relativo ao html

# ---------------- helpers ----------------
def esc(t): return html.escape(str(t), quote=True)

def brl(v):
    return ("R$ " + f"{v:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")

# Variante -> classe de cor do selo
VAR_CLS = {
    "Golden Baller": "b-gold", "Eternos 22": "b-gold", "Momemtum": "b-gold",
    "Limited Edition": "b-holo",
    "Icon": "b-blue", "Fan Favourite": "b-blue", "Master Rookies": "b-blue",
    "Contenders": "b-red", "Goal Machines": "b-red",
    "Top Keepers": "b-teal", "Defensive Rocks": "b-teal", "Midfield Maestros": "b-teal",
    "Team logo": "b-teal", "Official Emblem": "b-teal", "Official Mascot": "b-teal",
    "base": "",
}
# texto curto do selo (default = a propria variante)
BADGE_LBL = {
    "Limited Edition": "Limited", "Midfield Maestros": "Maestro", "Defensive Rocks": "Def. Rock",
    "Goal Machines": "Goal Machine", "Master Rookies": "Rookie", "Official Emblem": "Emblem",
    "Official Mascot": "Mascot", "Momemtum": "Momentum", "Golden Baller": "Golden Baller",
}
# nome bonito da variante para o subtitulo (base -> usa a posicao)
VAR_DISP = {"base": "", "Momemtum": "Momentum"}
POS_LBL  = {"GOL": "Goleiro", "DEF": "Defensor", "MEI": "Meio-campo", "ATA": "Atacante", "": ""}
# selecoes que nao sao pais (vao pro fim)
ESPECIAIS = {"Contenders", "FIFA"}

def img_src(n):
    return f"{IMG_DIR}/{n}.webp"

# ---------------- carrega dados ----------------
with open(ARQ_DADOS, encoding="utf-8") as f:
    RAW = json.load(f)
COLECAO = RAW.get("colecao", REFERENCIA)
CARDS = RAW["cartas"]          # [{n, cod, jog, sel, var, pos, rar, img}, ...]
if CARD_MAX is not None:
    CARDS = [c for c in CARDS if c["n"] <= CARD_MAX]
total = len(CARDS)
com_foto = sum(1 for c in CARDS if c["img"])

# categorias por SELECAO, na ordem de primeira aparicao; Contenders/FIFA no fim
ORDER, GRUPOS = [], {}
for c in CARDS:
    key = c["sel"]
    if key not in GRUPOS:
        GRUPOS[key] = []
        ORDER.append(key)
    GRUPOS[key].append(c)
for k in list(ESPECIAIS):
    if k in ORDER:
        ORDER.remove(k); ORDER.append(k)

n_paises = len([k for k in ORDER if k not in ESPECIAIS])

def subtitulo_card(c):
    if c["var"] == "base":
        return POS_LBL.get(c["pos"], "")
    return VAR_DISP.get(c["var"], c["var"])

# ---------------- render de card ----------------
def card_html(c):
    n, cod, jog, sel, var = c["n"], c["cod"], c["jog"], c["sel"], c["var"]
    cls = VAR_CLS.get(var, "b-blue" if c["rar"] != "common" else "")
    blbl = BADGE_LBL.get(var, var)
    badge = f'<span class="badge {cls}">{esc(blbl)}</span>' if cls else ""
    sub = subtitulo_card(c)
    idx = f"{cod} {n} {jog} {sel} {var}".lower()
    if c["img"]:
        media = f'<div class="media"><img loading="lazy" src="{esc(img_src(n))}" alt="{esc(jog)} ({esc(sel)})"></div>'
    else:
        media = f'<div class="media"><div class="ph"><span>{esc(jog[:1])}</span></div></div>'
    return f'''<div class="card" data-cod="{esc(cod)}" data-n="{esc(idx)}" data-nome="{esc(jog)}" data-preco="{PRECO_UNIT}">
  <div class="mediawrap">{media}{badge}</div>
  <div class="info">
    <div class="nome">{esc(jog)}</div>
    <div class="eq">{esc(sub)}</div>
    <div class="row"><span class="cod">{esc(cod)}</span><span class="preco">{brl(PRECO_UNIT).replace("R$ ","R$")}</span></div>
    <div class="addwrap">
      <button class="addbtn" type="button" data-add><i class="ti ti-plus"></i> <span>Adicionar</span></button>
      <div class="qtybox"><button type="button" data-dec><i class="ti ti-minus"></i></button><span data-qty>1</span><button type="button" data-inc><i class="ti ti-plus"></i></button></div>
    </div>
  </div>
</div>'''

def sec_icon(key):
    return "ti-star" if key in ESPECIAIS else "ti-flag"

secoes, nav = [], []
for i, key in enumerate(ORDER):
    lst = GRUPOS[key]
    sid = "sec" + str(i)
    corpo = '<div class="grid">' + "".join(card_html(c) for c in lst) + "</div>"
    ic = sec_icon(key)
    nav.append(f'<a href="#{sid}"><i class="ti {ic}"></i>{esc(key)} <b>{len(lst)}</b></a>')
    coll = "" if i < 3 else " collapsed"   # 3 primeiras abertas
    secoes.append(f'''<section id="{sid}" class="{coll.strip()}">
      <h2 class="sec-h"><i class="ti {ic}"></i>{esc(key)}<span class="qt">{len(lst)} cards</span><i class="ti ti-chevron-down chev"></i></h2>
      <div class="sec-body">{corpo}</div>
    </section>''')

n_times = n_paises   # usado no template (stat)

# lista para o "pedido rapido" (ordem numerica da colecao) -> [codigo, jogador, numero]
fast_json = json.dumps([[c["cod"], c["jog"], c["n"]] for c in CARDS], ensure_ascii=False)

# ---------------- TEMPLATE ----------------
HTML = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(MARCA)} — Catálogo de Cards</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.7.0/dist/tabler-icons.min.css" rel="stylesheet">
<style>
:root{{--bg:#0f1420;--bg2:#f3f5fb;--ink:#141a26;--navy:#0b2a53;--navy2:#123f7a;--blue:#1f6fe0;--blue-l:#e2ecfb;--gold:#e7b53c;--card:#fff;--line:#e2e7f0;--mut:#5f6b80}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg2);color:var(--ink);line-height:1.45}}
img{{display:block;width:100%;height:100%;object-fit:contain}}
a{{text-decoration:none;color:inherit}}
.wrap{{max-width:900px;margin:0 auto;padding:0 14px 60px}}

/* CAPA */
.capa{{background:linear-gradient(160deg,#0b2a53,#123f7a 55%,#1f6fe0);color:#fff;text-align:center;padding:44px 20px 38px;border-radius:0 0 26px 26px;position:relative;overflow:hidden}}
.capa::after{{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 82% -10%,rgba(231,181,60,.25),transparent 46%)}}
.capa>*{{position:relative;z-index:1}}
.logo{{font-family:Georgia,'Times New Roman',serif;font-size:13px;letter-spacing:6px;color:var(--gold);text-transform:uppercase}}
.capa h1{{font-family:Georgia,serif;font-size:38px;font-weight:600;margin:8px 0 4px;letter-spacing:.5px}}
.capa .sub{{color:#cfe0f7;font-size:14px;max-width:460px;margin:6px auto 0}}
.capa .selo{{display:inline-block;margin-top:16px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);color:#fff;font-size:12px;letter-spacing:1px;padding:7px 16px;border-radius:30px}}
.capa .atualizado{{margin-top:8px;color:rgba(255,255,255,.78);font-size:11px;letter-spacing:.5px}}
.capa .atualizado i{{font-size:12px;vertical-align:-1px;margin-right:4px}}
.stats{{display:flex;gap:10px;justify-content:center;margin-top:20px;flex-wrap:wrap}}
.stats div{{background:rgba(0,0,0,.2);border-radius:12px;padding:8px 14px;min-width:84px}}
.stats b{{display:block;font-size:20px;font-family:Georgia,serif}}
.stats span{{font-size:11px;color:#bcd2f0}}

/* BUSCA + NAV */
.tools{{position:sticky;top:0;z-index:20;background:var(--bg2);padding:12px 0 8px;margin-top:6px}}
.search{{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:30px;padding:10px 16px;box-shadow:0 2px 10px rgba(11,42,83,.06)}}
.search i{{color:var(--blue)}}
.search input{{border:0;outline:0;flex:1;font-size:15px;background:transparent;color:var(--ink)}}
.filtros{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}}
.viewtoggle{{display:flex;gap:0;background:#fff;border:1px solid var(--line);border-radius:30px;padding:3px;width:fit-content}}
.viewtoggle button{{border:0;background:transparent;color:var(--mut);font-size:12.5px;font-weight:600;padding:7px 15px;border-radius:30px;display:flex;align-items:center;gap:6px;cursor:pointer}}
.viewtoggle button.active{{background:var(--navy);color:#fff}}
.viewtoggle i{{font-size:16px}}
.rarsel{{position:relative;display:flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--line);border-radius:30px;padding:0 6px 0 13px}}
.rarsel i{{color:var(--blue);font-size:16px}}
.rarsel select{{border:0;outline:0;background:transparent;font-size:12.5px;font-weight:600;color:var(--ink);padding:8px 6px;cursor:pointer;font-family:inherit}}
.nav{{display:flex;gap:8px;overflow-x:auto;padding:10px 0 2px;-webkit-overflow-scrolling:touch}}
.nav a{{white-space:nowrap;font-size:12.5px;color:var(--navy);background:#fff;border:1px solid var(--line);padding:7px 13px;border-radius:30px;display:flex;align-items:center;gap:6px}}
.nav a b{{background:var(--blue-l);color:var(--navy2);border-radius:20px;padding:1px 7px;font-size:11px}}
.nav a i{{color:var(--blue)}}

/* SECOES */
section{{margin-top:24px;scroll-margin-top:120px}}
h2{{display:flex;align-items:center;gap:10px;font-family:Georgia,serif;font-size:21px;color:var(--navy);font-weight:600;padding-bottom:8px;border-bottom:2px solid var(--blue-l)}}
h2 i{{color:var(--blue)}}
h2 .qt{{margin-left:auto;font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:400;color:var(--mut)}}

/* GRID CARDS */
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-top:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;transition:.15s;box-shadow:0 2px 8px rgba(11,42,83,.05)}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 20px rgba(11,42,83,.14)}}
.mediawrap{{position:relative}}
.media{{position:relative;height:184px;background:linear-gradient(160deg,#eef3fb,#fff);padding:10px;border-bottom:1px solid var(--line)}}
.ph{{display:flex;align-items:center;justify-content:center;height:100%;background:linear-gradient(135deg,#e6eefb,#f3f7fd);border-radius:10px}}
.ph span{{font-family:Georgia,serif;font-size:40px;color:var(--blue);opacity:.55}}
.badge{{position:absolute;top:8px;left:8px;font-size:9.5px;font-weight:700;letter-spacing:.4px;padding:3px 9px;border-radius:20px;text-transform:uppercase;color:#fff;box-shadow:0 2px 6px rgba(0,0,0,.2)}}
.b-gold{{background:linear-gradient(135deg,#e7b53c,#b8860b);color:#2c1e00}}
.b-blue{{background:linear-gradient(135deg,#2f8bff,#1f6fe0)}}
.b-red{{background:linear-gradient(135deg,#ff5a4d,#e0322a)}}
.b-teal{{background:linear-gradient(135deg,#18c2ad,#0f9d8c)}}
.b-holo{{background:linear-gradient(120deg,#a855f7,#ec4899,#f59e0b,#22d3ee);color:#1a0033}}
.info{{padding:11px 12px 13px;display:flex;flex-direction:column;gap:5px;flex:1}}
.nome{{font-size:13.5px;font-weight:600;line-height:1.25;min-height:34px}}
.eq{{font-size:11.5px;color:var(--blue);font-style:italic}}
.row{{display:flex;align-items:baseline;justify-content:space-between;margin-top:auto;gap:6px}}
.cod{{font-size:11px;color:var(--mut)}}
.preco{{font-family:Georgia,serif;font-size:18px;font-weight:700;color:var(--navy)}}

/* ADICIONAR / STEPPER */
.addwrap{{margin-top:4px}}
.addbtn{{display:flex;width:100%;align-items:center;justify-content:center;gap:6px;background:#25d366;color:#063b1c;font-size:12.5px;font-weight:600;padding:11px 8px;min-height:44px;border:0;border-radius:9px;cursor:pointer;transition:.12s}}
.addbtn:hover{{background:#1fc25b}}
.addbtn i{{font-size:16px}}
.qtybox{{display:none;align-items:center;justify-content:space-between;gap:6px;background:#eaf7ee;border:1px solid #bfe6cb;border-radius:9px;padding:4px;margin-top:4px}}
.qtybox button{{width:40px;height:40px;border:0;border-radius:7px;background:#25d366;color:#063b1c;font-size:16px;display:flex;align-items:center;justify-content:center;cursor:pointer}}
.qtybox button:hover{{background:#1fc25b}}
.qtybox [data-qty]{{font-weight:700;color:#0a3a1c;min-width:22px;text-align:center;font-size:15px}}
.incart .addbtn{{display:none}}
.incart .qtybox{{display:flex}}
.incart.card{{outline:2px solid #25d366;outline-offset:-2px}}

.empty{{text-align:center;color:var(--mut);padding:40px 0;font-size:15px;display:none}}

/* RODAPE */
footer{{background:var(--navy);color:#fff;border-radius:22px;margin-top:42px;padding:30px 22px;text-align:center}}
footer h3{{font-family:Georgia,serif;font-size:24px;color:#fff;margin-bottom:4px}}
footer .fsub{{color:#bcd2f0;font-size:13px;margin-bottom:18px}}
.fcontacts{{display:flex;flex-direction:column;gap:11px;max-width:340px;margin:0 auto}}
.fcontacts a,.fcontacts div{{display:flex;align-items:center;gap:11px;justify-content:center;color:#fff;font-size:14px;background:rgba(255,255,255,.1);border-radius:11px;padding:11px 14px}}
.fcontacts i{{color:var(--gold);font-size:18px}}
.fbtn{{background:#25d366!important;color:#063b1c!important;font-weight:700!important;margin-top:4px}}
.note{{margin-top:18px;color:#9db8dc;font-size:11px;line-height:1.5}}
.top{{position:fixed;right:16px;bottom:16px;z-index:30;background:var(--navy);color:#fff;width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.25);font-size:20px}}
body.has-cart .top{{bottom:80px}}

/* ACORDEAO */
.sec-h{{cursor:pointer;user-select:none}}
.chev{{margin-left:10px;color:var(--blue);font-size:18px;transition:transform .2s}}
.collapsed .chev{{transform:rotate(-90deg)}}
.collapsed .sec-body{{display:none}}
.searching .sec-body{{display:block!important}}

/* MODO LISTA */
.listview .grid{{grid-template-columns:1fr;gap:8px}}
@media(min-width:560px){{.listview .grid{{grid-template-columns:1fr 1fr}}}}
.listview .card{{flex-direction:row;align-items:center;border-radius:12px;padding:6px 10px 6px 6px;box-shadow:none}}
.listview .card:hover{{transform:none;box-shadow:0 2px 8px rgba(11,42,83,.08)}}
.listview .mediawrap{{width:46px;height:60px;flex:none}}
.listview .media{{width:46px;height:60px;padding:2px;border:0;border-radius:8px}}
.listview .badge{{display:none}}
.listview .info{{flex-direction:row;align-items:center;gap:10px;padding:0 0 0 10px}}
.listview .nome{{min-height:0;font-size:13px;flex:1}}
.listview .eq{{display:none}}
.listview .row{{flex:none;margin:0;flex-direction:column;align-items:flex-end;gap:0}}
.listview .cod{{display:none}}
.listview .preco{{font-size:15.5px}}
.listview .addwrap{{margin:0;flex:none}}
.listview .addbtn{{width:44px;min-height:44px;padding:0;font-size:0}}
.listview .addbtn i{{font-size:18px}}
.listview .addbtn span{{display:none}}
.listview .qtybox{{margin:0;padding:3px}}
.listview .qtybox button{{width:38px;height:38px;font-size:15px}}
.listview .qtybox [data-qty]{{min-width:18px;font-size:13px}}

/* BARRA + PAINEL DO CARRINHO */
.cartbar{{position:fixed;left:0;right:0;bottom:0;z-index:40;background:#fff;border-top:1px solid var(--line);box-shadow:0 -4px 16px rgba(11,42,83,.14)}}
.cartbar[hidden]{{display:none}}
.cb-inner{{max-width:900px;margin:0 auto;display:flex;gap:10px;align-items:center;padding:10px 14px}}
.cart-info{{flex:1;text-align:left;background:transparent;border:0;color:var(--navy);font-weight:600;font-size:13px;display:flex;align-items:center;gap:7px;cursor:pointer}}
.cart-info .ci-ic{{position:relative;font-size:22px;color:var(--blue)}}
.cart-info b{{font-family:Georgia,serif;font-size:17px}}
.cart-go{{background:#25d366;color:#063b1c;border:0;border-radius:11px;font-size:14px;font-weight:700;padding:12px 16px;display:flex;align-items:center;gap:7px;cursor:pointer}}
.cart-go:hover{{background:#1fc25b}}
.cart-go i{{font-size:18px}}
.overlay{{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:44;opacity:0;pointer-events:none;transition:.25s}}
.overlay.show{{opacity:1;pointer-events:auto}}
.cartpanel{{position:fixed;left:0;right:0;bottom:0;z-index:45;background:#fff;border-radius:18px 18px 0 0;box-shadow:0 -8px 30px rgba(0,0,0,.28);max-width:900px;margin:0 auto;max-height:78vh;display:flex;flex-direction:column;transform:translateY(110%);transition:transform .25s}}
.cartpanel.open{{transform:translateY(0)}}
.cp-head{{display:flex;align-items:center;justify-content:space-between;padding:16px 18px 12px;border-bottom:1px solid var(--line);cursor:pointer}}
.cp-head h4{{font-family:Georgia,serif;font-size:19px;color:var(--navy);font-weight:600}}
.cp-x{{background:transparent;border:0;font-size:24px;color:var(--mut);cursor:pointer;line-height:1}}
.cp-list{{overflow-y:auto;padding:4px 16px}}
.cp-empty{{text-align:center;color:var(--mut);padding:30px 0;font-size:14px}}
.cp-row{{display:flex;align-items:center;gap:10px;padding:11px 0;border-bottom:1px solid #eef2f8}}
.cp-n{{flex:1;font-size:13px;font-weight:600;line-height:1.25}}
.cp-n small{{display:block;color:var(--mut);font-weight:400;font-size:11px}}
.cp-line{{font-family:Georgia,serif;font-weight:700;color:var(--navy);font-size:14px;white-space:nowrap}}
.cp-rem{{background:transparent;border:0;color:#c0394b;font-size:18px;cursor:pointer;padding:4px}}
.cp-foot{{padding:14px 18px 18px;border-top:1px solid var(--line);background:#fff}}
.cp-total{{display:flex;justify-content:space-between;align-items:baseline;font-size:15px;margin-bottom:12px;color:var(--ink)}}
.cp-total b{{font-family:Georgia,serif;font-size:22px;color:var(--navy)}}
.cp-nome{{width:100%;border:1px solid var(--line);border-radius:11px;padding:12px 14px;font-size:15px;color:var(--ink);outline:none;margin-bottom:10px;font-family:inherit}}
.cp-nome::placeholder{{color:var(--mut)}}
.cp-nome:focus{{border-color:var(--blue)}}
.cp-nome.err{{border-color:#e24b4a;background:#fdeceb}}
.cp-go{{width:100%;background:#25d366;color:#063b1c;border:0;border-radius:12px;font-size:15px;font-weight:700;padding:14px;display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer}}
.cp-go:hover{{background:#1fc25b}}
.cp-go i{{font-size:19px}}
.cp-safe{{margin:10px 0 0;text-align:center;font-size:12px;color:var(--mut);line-height:1.55}}
.cp-safe i{{color:#25d366;font-size:14px;vertical-align:-2px;margin-right:4px}}
.cp-clear{{display:block;margin:10px auto 0;background:transparent;border:0;color:var(--mut);font-size:12px;text-decoration:underline;cursor:pointer}}

/* LIGHTBOX */
.media img{{cursor:zoom-in}}
.lb{{position:fixed;inset:0;z-index:200;background:rgba(6,12,22,.96);display:none;align-items:center;justify-content:center;overflow:hidden;touch-action:none;-webkit-user-select:none;user-select:none}}
.lb.open{{display:flex}}
.lb img{{max-width:100vw;max-height:100vh;width:auto;height:auto;object-fit:contain;transform-origin:0 0;-webkit-user-drag:none}}
.lb.zoomed img{{cursor:grab}}
.lb-x{{position:absolute;top:14px;right:16px;z-index:6;width:44px;height:44px;border:0;border-radius:50%;background:rgba(0,0,0,.45);color:#fff;font-size:24px;line-height:1;display:flex;align-items:center;justify-content:center;cursor:pointer}}
.lb-hint{{position:absolute;bottom:18px;left:0;right:0;text-align:center;color:rgba(255,255,255,.65);font-size:12px;pointer-events:none;transition:opacity .4s}}
.lb.zoomed .lb-hint{{opacity:0}}

/* BOTAO PEDIDO RAPIDO (na capa) */
.fast-btn{{margin:20px auto 0;display:flex;align-items:center;gap:9px;background:linear-gradient(135deg,#f0c94a,#e7b53c);color:#2c1e00;border:0;border-radius:30px;font-size:15px;font-weight:800;padding:14px 24px;cursor:pointer;box-shadow:0 8px 22px rgba(231,181,60,.4);letter-spacing:.2px}}
.fast-btn i{{font-size:20px}}
.fast-btn:hover{{filter:brightness(1.05);transform:translateY(-1px)}}
.fast-btn:active{{transform:translateY(0)}}

/* MODAL PEDIDO RAPIDO */
.fastmodal{{position:fixed;inset:0;z-index:120;background:var(--bg2);display:none;flex-direction:column}}
.fastmodal.open{{display:flex}}
.fm-head{{display:flex;align-items:center;justify-content:space-between;padding:15px 16px 13px;background:var(--navy);color:#fff}}
.fm-title{{display:flex;align-items:center;gap:8px;font-family:Georgia,serif;font-size:19px}}
.fm-title i{{color:var(--gold)}}
.fm-x{{background:transparent;border:0;color:#fff;font-size:30px;line-height:1;cursor:pointer;padding:0 4px}}
.fm-search{{display:flex;align-items:center;gap:9px;background:#fff;border-bottom:1px solid var(--line);padding:12px 16px}}
.fm-search i{{color:var(--blue);font-size:19px}}
.fm-search input{{border:0;outline:0;flex:1;font-size:16px;background:transparent;color:var(--ink)}}
.fm-list{{flex:1;overflow-y:auto;padding:6px 10px 12px;-webkit-overflow-scrolling:touch}}
.frow{{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin-top:7px}}
.frow.incart{{border-color:#25d366;background:#f4fcf6}}
.fr-n{{font-family:Georgia,serif;font-weight:700;color:var(--navy);font-size:13px;min-width:52px}}
.fr-nome{{flex:1;font-size:13.5px;font-weight:600;line-height:1.2}}
.fr-add{{width:46px;height:40px;border:0;border-radius:8px;background:#25d366;color:#063b1c;font-size:22px;display:flex;align-items:center;justify-content:center;cursor:pointer;flex:none}}
.fr-add:hover{{background:#1fc25b}}
.fr-qty{{display:none;align-items:center;gap:4px;background:#eaf7ee;border:1px solid #bfe6cb;border-radius:8px;padding:3px;flex:none}}
.fr-qty button{{width:36px;height:34px;border:0;border-radius:6px;background:#25d366;color:#063b1c;font-size:16px;display:flex;align-items:center;justify-content:center;cursor:pointer}}
.fr-qty [data-qty]{{min-width:22px;text-align:center;font-weight:700;color:#0a3a1c;font-size:14px}}
.frow.incart .fr-add{{display:none}}
.frow.incart .fr-qty{{display:flex}}
.fm-empty{{text-align:center;color:var(--mut);padding:30px 0;font-size:14px}}
.fm-foot{{padding:12px 16px calc(14px + env(safe-area-inset-bottom));border-top:1px solid var(--line);background:#fff;box-shadow:0 -4px 16px rgba(11,42,83,.12)}}
.fm-total{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;font-size:14px;color:var(--mut)}}
.fm-total b{{font-family:Georgia,serif;font-size:21px;color:var(--navy)}}
</style>
</head>
<body>
<div class="capa">
  <div class="logo">Trading Cards</div>
  <h1>{esc(MARCA)}</h1>
  <p class="sub">{esc(SUBTITULO)}</p>
  <div class="selo">{esc(REFERENCIA)}</div>
  <div class="atualizado"><i class="ti ti-calendar-check"></i>Atualizado em {esc(ATUALIZADO)}</div>
  <div class="stats">
    <div><b>{total}</b><span>cards</span></div>
    <div><b>{n_times}</b><span>seleções</span></div>
    <div><b>{brl(PRECO_UNIT).replace('R$ ','R$')}</b><span>cada</span></div>
  </div>
  <button class="fast-btn" id="fastOpen" type="button"><i class="ti ti-bolt"></i> Fazer pedido — modo rápido</button>
</div>

<div class="wrap">
  <div class="tools">
    <label class="search"><i class="ti ti-search"></i><input id="q" type="search" placeholder="Buscar por jogador, seleção, código..."></label>
    <div class="filtros">
      <div class="viewtoggle">
        <button id="vCards" class="active" type="button"><i class="ti ti-layout-grid"></i> Cards</button>
        <button id="vList" type="button"><i class="ti ti-list"></i> Lista</button>
      </div>
      <label class="rarsel"><i class="ti ti-filter"></i>
        <select id="rar">
          <option value="">Todas as raridades</option>
          <option value="core / team mate">Base (Team Mate)</option>
          <option value="fans / emblem">Emblem</option>
          <option value="fans / crowd hero">Crowd Hero</option>
          <option value="rare / golden baller">Golden Baller</option>
          <option value="x-rare / invincible">Invincible</option>
          <option value="power / titan">Power · Titan</option>
          <option value="power / magician">Power · Magician</option>
          <option value="power / goal machine">Power · Goal Machine</option>
          <option value="gold / top keeper">Gold · Top Keeper</option>
          <option value="gold / game changer">Gold · Game Changer</option>
          <option value="world / new hero">World · New Hero</option>
          <option value="world / legend">World · Legend</option>
          <option value="limited edition">Limited Edition</option>
        </select>
      </label>
    </div>
    <div class="nav">{''.join(nav)}</div>
  </div>

  <p class="empty" id="empty">Nenhuma card encontrada. Tente outro termo.</p>

  {''.join(secoes)}

  <footer>
    <h3>{esc(MARCA)}</h3>
    <p class="fsub">Faça seu pedido pelo WhatsApp · cards avulsas</p>
    <div class="fcontacts">
      <a class="fbtn" href="https://wa.me/{WHATSAPP}" target="_blank"><i class="ti ti-brand-whatsapp"></i> {esc(WHATSAPP_F)}</a>
      <a href="https://instagram.com/{esc(INSTAGRAM)}" target="_blank"><i class="ti ti-brand-instagram"></i> @{esc(INSTAGRAM)}</a>
      <div><i class="ti ti-map-pin"></i> {esc(ENDERECO)}</div>
    </div>
    <p class="note">Imagens meramente ilustrativas. Coleção {esc(REFERENCIA)}. Preços sujeitos a alteração. Panini e FIFA são marcas de seus respectivos titulares — cards avulsas para troca/venda entre colecionadores.</p>
  </footer>
</div>
<a href="#" class="top" aria-label="Voltar ao topo"><i class="ti ti-arrow-up"></i></a>

<div class="cartbar" id="cartbar" hidden><div class="cb-inner">
  <button class="cart-info" id="cInfo" type="button"><i class="ti ti-shopping-cart ci-ic"></i><span><b id="cCount">0</b> cards · <span id="cTotal">R$ 0,00</span></span></button>
  <button class="cart-go" id="cGo" type="button">Fechar Pedido <i class="ti ti-brand-whatsapp"></i></button>
</div></div>

<div class="overlay" id="overlay"></div>
<div class="cartpanel" id="cartpanel">
  <div class="cp-head" id="cpHead"><h4>Seu pedido</h4><button class="cp-x" id="cpClose" type="button">&times;</button></div>
  <div class="cp-list" id="cpList"></div>
  <div class="cp-foot">
    <div class="cp-total"><span>Total do pedido</span><b id="cpTotal">R$ 0,00</b></div>
    <input id="cpNome" class="cp-nome" type="text" placeholder="Seu nome (para identificar o pedido)" autocomplete="name">
    <button class="cp-go" id="cpGo" type="button"><i class="ti ti-brand-whatsapp"></i> Fechar Pedido no WhatsApp</button>
    <p class="cp-safe"><i class="ti ti-lock"></i> Abre o WhatsApp com seu pedido pronto.<br>Você confirma tudo na conversa.</p>
    <button class="cp-clear" id="cpClear" type="button">Limpar pedido</button>
  </div>
</div>

<div class="fastmodal" id="fastModal">
  <div class="fm-head">
    <div class="fm-title"><i class="ti ti-bolt"></i> Pedido rápido</div>
    <button class="fm-x" id="fastClose" type="button" aria-label="Fechar">&times;</button>
  </div>
  <label class="fm-search"><i class="ti ti-search"></i><input id="fastQ" type="search" inputmode="search" placeholder="Nº ou nome do jogador..."></label>
  <div class="fm-list" id="fastList"></div>
  <div class="fm-foot">
    <div class="fm-total"><span id="fastCount">0 cards</span><b id="fastTotal">R$ 0,00</b></div>
    <input id="fastNome" class="cp-nome" type="text" placeholder="Seu nome (para identificar o pedido)" autocomplete="name">
    <button class="cp-go" id="fastGo" type="button"><i class="ti ti-brand-whatsapp"></i> Fechar Pedido no WhatsApp</button>
  </div>
</div>

<div class="lb" id="lb">
  <button class="lb-x" id="lbX" type="button" aria-label="Fechar">&times;</button>
  <img id="lbImg" src="" alt="" draggable="false">
  <div class="lb-hint">Pinça ou toque duplo para dar zoom</div>
</div>

<script>
const WA="{WHATSAPP}";
const PRECO={PRECO_UNIT};
const FAST={fast_json};
const BRL=new Intl.NumberFormat('pt-BR',{{style:'currency',currency:'BRL'}});
const fmt=v=>BRL.format(v);
const wrap=document.querySelector('.wrap');

const q=document.getElementById('q'),empty=document.getElementById('empty'),rar=document.getElementById('rar');
const items=[...document.querySelectorAll('[data-n]')],secs=[...document.querySelectorAll('section')];
function applyFilter(){{
  const t=q.value.toLowerCase().trim();
  const rv=rar.value;
  let any=false;const active=!!t||!!rv;
  wrap.classList.toggle('searching', active);
  items.forEach(el=>{{
    const m=(!t||el.dataset.n.includes(t))&&(!rv||el.dataset.n.includes(rv));
    el.style.display=m?'':'none';if(m)any=true;
  }});
  secs.forEach(s=>{{const vis=[...s.querySelectorAll('[data-n]')].some(e=>e.style.display!=='none');s.style.display=vis?'':'none';}});
  empty.style.display=any?'none':'block';
}}
q.addEventListener('input',applyFilter);
rar.addEventListener('change',applyFilter);

document.querySelectorAll('.sec-h').forEach(h=>h.addEventListener('click',()=>h.closest('section').classList.toggle('collapsed')));

const vC=document.getElementById('vCards'),vL=document.getElementById('vList');
vC.onclick=()=>{{wrap.classList.remove('listview');vC.classList.add('active');vL.classList.remove('active');}};
vL.onclick=()=>{{wrap.classList.add('listview');vL.classList.add('active');vC.classList.remove('active');}};

const cart={{}};
const LS='pedido_cards_v1';
function save(){{try{{localStorage.setItem(LS,JSON.stringify(cart));}}catch(e){{}}}}
const bar=document.getElementById('cartbar'),panel=document.getElementById('cartpanel'),overlay=document.getElementById('overlay');
const cCount=document.getElementById('cCount'),cTotal=document.getElementById('cTotal'),cpList=document.getElementById('cpList'),cpTotal=document.getElementById('cpTotal');
const fastModal=document.getElementById('fastModal'),fastList=document.getElementById('fastList'),fastCount=document.getElementById('fastCount'),fastTotalEl=document.getElementById('fastTotal');

function syncItem(cod){{
  document.querySelectorAll('[data-cod="'+CSS.escape(cod)+'"]').forEach(el=>{{
    if(!el.classList.contains('card')&&!el.classList.contains('frow'))return;
    const qy=cart[cod]?cart[cod].qty:0;
    el.classList.toggle('incart', qy>0);
    const s=el.querySelector('[data-qty]'); if(s)s.textContent=qy||1;
  }});
}}
function addItem(el){{
  const cod=el.dataset.cod;
  if(cart[cod])cart[cod].qty++;
  else cart[cod]={{nome:el.dataset.nome,preco:parseFloat(el.dataset.preco),qty:1}};
  syncItem(cod);render();
}}
function chg(cod,d){{
  if(!cart[cod])return;
  cart[cod].qty+=d;
  if(cart[cod].qty<=0)delete cart[cod];
  syncItem(cod);render();
}}
function totals(){{let n=0,t=0;for(const k in cart){{n+=cart[k].qty;t+=cart[k].qty*cart[k].preco;}}return{{n:n,t:t}};}}
function render(){{
  save();
  const tt=totals();
  cCount.textContent=tt.n;cTotal.textContent=fmt(tt.t);
  if(fastCount){{fastCount.textContent=tt.n+(tt.n===1?' card':' cards');fastTotalEl.textContent=fmt(tt.t);}}
  bar.hidden=tt.n===0;document.body.classList.toggle('has-cart',tt.n>0);
  if(tt.n===0)closePanel();
  cpTotal.textContent=fmt(tt.t);
  const ks=Object.keys(cart);
  cpList.innerHTML=ks.length?ks.map(cod=>{{const it=cart[cod];const line=it.qty*it.preco;
    return '<div class="cp-row" data-cod="'+cod+'"><div class="cp-n">'+it.nome+'<small>'+cod+' · '+fmt(it.preco)+(it.qty>1?' · '+it.qty+'x':'')+'</small></div>'+
      '<div class="qtybox" style="display:flex"><button type="button" data-dec><i class="ti ti-minus"></i></button><span>'+it.qty+'</span><button type="button" data-inc><i class="ti ti-plus"></i></button></div>'+
      '<span class="cp-line">'+fmt(line)+'</span><button class="cp-rem" type="button" data-rem aria-label="remover"><i class="ti ti-trash"></i></button></div>';
  }}).join(''):'<p class="cp-empty">Seu pedido está vazio. Toque em + Adicionar nas cards.</p>';
}}
function openPanel(){{if(Object.keys(cart).length){{panel.classList.add('open');overlay.classList.add('show');}}}}
function closePanel(){{panel.classList.remove('open');overlay.classList.remove('show');}}

document.addEventListener('click',e=>{{
  const add=e.target.closest('[data-add]'),inc=e.target.closest('[data-inc]'),dec=e.target.closest('[data-dec]'),rem=e.target.closest('[data-rem]');
  if(add){{addItem(add.closest('[data-cod]'));}}
  else if(inc){{chg(inc.closest('[data-cod]').dataset.cod,1);}}
  else if(dec){{chg(dec.closest('[data-cod]').dataset.cod,-1);}}
  else if(rem){{const cod=rem.closest('[data-cod]').dataset.cod;delete cart[cod];syncItem(cod);render();}}
}});
document.getElementById('cInfo').onclick=()=>{{panel.classList.contains('open')?closePanel():openPanel();}};
document.getElementById('cpHead').onclick=closePanel;
overlay.onclick=closePanel;
document.getElementById('cpClose').onclick=closePanel;
document.getElementById('cpClear').onclick=()=>{{const ks=Object.keys(cart);ks.forEach(c=>delete cart[c]);ks.forEach(syncItem);render();}};

const cpNome=document.getElementById('cpNome');
cpNome.addEventListener('input',()=>cpNome.classList.remove('err'));
function fechar(){{
  const ks=Object.keys(cart);if(!ks.length)return;
  const nome=cpNome.value.trim();
  if(!nome){{openPanel();cpNome.classList.add('err');cpNome.placeholder='Por favor, digite seu nome';cpNome.focus();return;}}
  const lines=ks.map(cod=>{{const it=cart[cod];const line=it.qty*it.preco;
    const qx=it.qty>1?' ('+it.qty+'x '+fmt(it.preco)+')':'';
    return cod+' - '+it.nome+qx+' - '+fmt(line);}});
  const tt=totals();
  const msg='*Pedido de Cards - '+nome+'*\\n\\n'+lines.join('\\n')+'\\n\\n*Total: '+fmt(tt.t)+'* ('+tt.n+' cards)';
  window.open('https://wa.me/'+WA+'?text='+encodeURIComponent(msg),'_blank');
}}
document.getElementById('cGo').onclick=()=>{{openPanel();setTimeout(()=>cpNome.focus(),250);}};
document.getElementById('cpGo').onclick=fechar;

/* LIGHTBOX zoom (pinca / toque duplo / roda) */
const lb=document.getElementById('lb'),lbImg=document.getElementById('lbImg'),lbX=document.getElementById('lbX');
const MINS=1,MAXS=4,DTS=2.6;
let s=1,tx=0,ty=0,base=null;
function applyT(anim){{lbImg.style.transition=anim?'transform .26s cubic-bezier(.22,.61,.36,1)':'none';lbImg.style.transform='translate('+tx+'px,'+ty+'px) scale('+s+')';lb.classList.toggle('zoomed',s>1.01);}}
function ensureBase(){{const r=lbImg.getBoundingClientRect();base={{l:r.left-tx,t:r.top-ty,w:r.width/s,h:r.height/s}};}}
function clampT(){{const W=innerWidth,H=innerHeight,rw=base.w*s,rh=base.h*s;
  tx=rw<=W?(W-rw)/2-base.l:Math.min(-base.l,Math.max(W-rw-base.l,tx));
  ty=rh<=H?(H-rh)/2-base.t:Math.min(-base.t,Math.max(H-rh-base.t,ty));}}
function zoomAt(px,py,ns){{ns=Math.min(MAXS,Math.max(MINS,ns));const cx=(px-base.l-tx)/s,cy=(py-base.t-ty)/s;s=ns;tx=px-base.l-cx*s;ty=py-base.t-cy*s;}}
function openLB(src,alt){{s=1;tx=0;ty=0;base=null;lbImg.alt=alt||'';lbImg.style.transition='none';lbImg.style.transform='';lbImg.src=src;
  lb.classList.remove('zoomed');lb.classList.add('open');document.body.style.overflow='hidden';
  const init=()=>{{ensureBase();applyT(false);}};
  if(lbImg.complete&&lbImg.naturalWidth)requestAnimationFrame(init);else lbImg.onload=()=>requestAnimationFrame(init);}}
function closeLB(){{lb.classList.remove('open','zoomed');document.body.style.overflow='';s=1;tx=0;ty=0;base=null;}}
function dist(t){{return Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY);}}
function mid(t){{return{{x:(t[0].clientX+t[1].clientX)/2,y:(t[0].clientY+t[1].clientY)/2}};}}
document.addEventListener('click',e=>{{const im=e.target.closest('.media img');if(im){{e.preventDefault();openLB(im.currentSrc||im.src,im.alt);}}}});
lbX.onclick=e=>{{e.stopPropagation();closeLB();}};
let pinch=false,panT=false,sStart=1,dStart=0,plx=0,ply=0,lastTap=0;
lb.addEventListener('touchstart',e=>{{if(!base)ensureBase();
  if(e.touches.length===2){{pinch=true;panT=false;sStart=s;dStart=dist(e.touches);applyT(false);}}
  else if(e.touches.length===1){{const now=e.timeStamp,t=e.touches[0];
    if(now-lastTap<300){{e.preventDefault();lastTap=0;if(s>1.01){{s=1;}}else zoomAt(t.clientX,t.clientY,DTS);clampT();applyT(true);}}
    else{{lastTap=now;panT=true;plx=t.clientX;ply=t.clientY;applyT(false);}}}}}},{{passive:false}});
lb.addEventListener('touchmove',e=>{{
  if(pinch&&e.touches.length===2){{e.preventDefault();const m=mid(e.touches);zoomAt(m.x,m.y,sStart*dist(e.touches)/dStart);applyT(false);}}
  else if(panT&&e.touches.length===1&&s>1){{e.preventDefault();const t=e.touches[0];tx+=t.clientX-plx;ty+=t.clientY-ply;plx=t.clientX;ply=t.clientY;applyT(false);}}}},{{passive:false}});
lb.addEventListener('touchend',e=>{{if(e.touches.length===0){{pinch=false;panT=false;if(base){{clampT();applyT(true);}}}}
  else if(e.touches.length===1&&pinch){{pinch=false;panT=true;plx=e.touches[0].clientX;ply=e.touches[0].clientY;}}}});
lb.addEventListener('dblclick',e=>{{if(!base)ensureBase();if(s>1.01){{s=1;}}else zoomAt(e.clientX,e.clientY,DTS);clampT();applyT(true);}});
lb.addEventListener('wheel',e=>{{e.preventDefault();if(!base)ensureBase();zoomAt(e.clientX,e.clientY,s*(e.deltaY<0?1.18:.85));clampT();applyT(false);}},{{passive:false}});
let md=false,mlx=0,mly=0;
lb.addEventListener('mousedown',e=>{{if(s>1){{md=true;mlx=e.clientX;mly=e.clientY;applyT(false);e.preventDefault();}}}});
addEventListener('mousemove',e=>{{if(md){{tx+=e.clientX-mlx;ty+=e.clientY-mly;mlx=e.clientX;mly=e.clientY;applyT(false);}}}});
addEventListener('mouseup',()=>{{if(md){{md=false;clampT();applyT(true);}}}});
addEventListener('resize',()=>{{if(lb.classList.contains('open')){{base=null;s=1;tx=0;ty=0;requestAnimationFrame(()=>{{ensureBase();applyT(false);}});}}}});

/* ---- PEDIDO RAPIDO ---- */
let fastBuilt=false;
function fEsc(t){{return String(t).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));}}
function buildFast(){{
  if(fastBuilt)return;fastBuilt=true;
  fastList.innerHTML=FAST.map(p=>{{
    const cod=p[0],nome=p[1],num=p[2];
    return '<div class="frow" data-cod="'+fEsc(cod)+'" data-nome="'+fEsc(nome)+'" data-preco="'+PRECO+'" data-fn="'+fEsc((num+' '+cod+' '+nome).toLowerCase())+'">'+
      '<span class="fr-n">'+fEsc(num)+'</span><span class="fr-nome">'+fEsc(nome)+'</span>'+
      '<button class="fr-add" type="button" data-add><i class="ti ti-plus"></i></button>'+
      '<div class="fr-qty"><button type="button" data-dec><i class="ti ti-minus"></i></button><span data-qty>1</span><button type="button" data-inc><i class="ti ti-plus"></i></button></div>'+
      '</div>';
  }}).join('')+'<p class="fm-empty" id="fastEmpty" style="display:none">Nada encontrado.</p>';
  Object.keys(cart).forEach(syncItem);
}}
function openFast(){{buildFast();fastModal.classList.add('open');document.body.style.overflow='hidden';}}
function closeFast(){{fastModal.classList.remove('open');document.body.style.overflow='';}}
document.getElementById('fastOpen').onclick=openFast;
document.getElementById('fastClose').onclick=closeFast;
document.getElementById('fastQ').addEventListener('input',e=>{{
  const t=e.target.value.toLowerCase().trim();let any=false;
  fastList.querySelectorAll('.frow').forEach(r=>{{const m=!t||r.dataset.fn.includes(t);r.style.display=m?'':'none';if(m)any=true;}});
  const emp=document.getElementById('fastEmpty');if(emp)emp.style.display=any?'none':'block';
}});
const fastNome=document.getElementById('fastNome');
fastNome.addEventListener('input',()=>fastNome.classList.remove('err'));
document.getElementById('fastGo').onclick=()=>{{
  const ks=Object.keys(cart);
  if(!ks.length){{document.getElementById('fastQ').focus();return;}}
  const nome=fastNome.value.trim();
  if(!nome){{fastNome.classList.add('err');fastNome.placeholder='Por favor, digite seu nome';fastNome.focus();return;}}
  const ord={{}},FNUM={{}};FAST.forEach((p,i)=>{{ord[p[0]]=i;FNUM[p[0]]=p[2];}});
  const lines=ks.slice().sort((a,b)=>(ord[a]==null?1e9:ord[a])-(ord[b]==null?1e9:ord[b]))
    .map(cod=>{{const it=cart[cod];const num=FNUM[cod]==null?cod:FNUM[cod];return num+' - '+it.nome+(it.qty>1?' ('+it.qty+'x)':'');}});
  const tt=totals();
  const msg='*Pedido rápido de Cards - '+nome+'*\\n\\n'+lines.join('\\n')+'\\n\\n*Total: '+tt.n+' cards - '+fmt(tt.t)+'*';
  window.open('https://wa.me/'+WA+'?text='+encodeURIComponent(msg),'_blank');
}};

/* restaura pedido salvo */
(function restore(){{try{{const s=JSON.parse(localStorage.getItem(LS)||'{{}}');for(const k in s)cart[k]=s[k];}}catch(e){{}}Object.keys(cart).forEach(syncItem);render();}})();
</script>
</body>
</html>'''

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write(HTML)

# index.html = copia
with open(os.path.join(os.path.dirname(SAIDA), "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML)

kb = os.path.getsize(SAIDA) / 1024
print(f"OK -> {SAIDA}")
print(f"   {total} cards | {com_foto} com foto | {total-com_foto} sem foto | {n_times} times | {kb:.0f} KB")
