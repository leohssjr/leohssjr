#!/usr/bin/env python3
"""Gera os SVGs do README (banner, cards de projeto e rodape).

O texto vira vetor porque o GitHub bloqueia fontes externas em SVG servido
como imagem. Para mudar algo (o semestre, por exemplo), edite as constantes
abaixo e rode:

    pip install fonttools brotli
    python3 assets/gerar_svgs.py
"""
import os
import tempfile
import urllib.request
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent
CACHE = Path(os.environ.get("FONT_CACHE", tempfile.gettempdir())) / "readme-fonts"
CDN = "https://cdn.jsdelivr.net/fontsource/fonts"
FONT_URLS = {
    "mono": f"{CDN}/jetbrains-mono@latest/latin-400-normal.woff2",
    "mono-bold": f"{CDN}/jetbrains-mono@latest/latin-700-normal.woff2",
    "sans": f"{CDN}/space-grotesk@latest/latin-400-normal.woff2",
    "sans-bold": f"{CDN}/space-grotesk@latest/latin-700-normal.woff2",
}

BG = "#0B1220"
PANEL = "#111B2E"
LINE = "#22314A"
SEPARADOR = "#3A4E6E"
TEXT = "#DCE6F2"
WHITE = "#FFFFFF"
MUTED = "#8496AE"
BLUE = "#5BA4FF"
ORACLE = "#FF7A59"

SEMESTRE = "8º"

PROJETOS = [
    {
        "arquivo": "projeto-marketplace.svg",
        "contexto": "TPPE · UnB · 2026/1",
        "nome": "MarketPlace",
        "texto": [
            "Marketplace feito em equipe. Tive 28 PRs",
            "aceitos, entre segurança da API, avaliações",
            "de produto e ranking de vendedores.",
        ],
        "stack": ["NestJS", "PostgreSQL", "React", "TypeScript"],
    },
    {
        "arquivo": "projeto-chamacontrol.svg",
        "contexto": "MDS · UnB · 2024/2",
        "nome": "ChamaControl",
        "texto": [
            "Consulta de focos de queimadas no Brasil por",
            "região, estado, município, ano e mês, com",
            "registros de satélite desde 2003.",
        ],
        "stack": ["JavaScript", "Express", "MySQL", "Docker"],
    },
    {
        "arquivo": "projeto-soccerstats.svg",
        "contexto": "Engenharia de dados",
        "nome": "SoccerStats",
        "texto": [
            "Dados de jogadores do Brasileirão, rodada a",
            "rodada, de 2014 a 2017, em arquitetura",
            "medalhão: bronze, silver e gold.",
        ],
        "stack": ["Python", "PostgreSQL", "Docker"],
    },
    {
        "arquivo": "projeto-touristeer.svg",
        "contexto": "UnB · 2025/1",
        "nome": "Touristeer",
        "texto": [
            "Um Waze para turistas explorarem novos",
            "destinos. Coordenei e desenvolvi o front-end",
            "do app.",
        ],
        "stack": ["JavaScript", "Python", "Vercel"],
    },
]


CONTATOS = {
    "contato-linkedin.svg": ("LinkedIn", BLUE),
    "contato-whatsapp.svg": ("WhatsApp", "#25D366"),
    "contato-gmail.svg": ("Gmail", ORACLE),
}


def carregar_fontes():
    CACHE.mkdir(parents=True, exist_ok=True)
    fontes = {}
    for nome, url in FONT_URLS.items():
        arquivo = CACHE / f"{nome}.woff2"
        if not arquivo.exists():
            pedido = urllib.request.Request(url, headers={"User-Agent": "gerar-svgs"})
            with urllib.request.urlopen(pedido) as resposta:
                arquivo.write_bytes(resposta.read())
        fonte = TTFont(arquivo)
        fontes[nome] = (fonte, fonte.getGlyphSet(), fonte.getBestCmap())
    return fontes


FONTES = carregar_fontes()


def largura(texto, fonte, tamanho):
    ttf, glifos, cmap = FONTES[fonte]
    escala = tamanho / ttf["head"].unitsPerEm
    return sum(glifos[cmap[ord(c)]].width for c in texto) * escala


def caminho(texto, x, y, tamanho, fonte="mono"):
    """Devolve o atributo d de um path com o texto desenhado em (x, y)."""
    ttf, glifos, cmap = FONTES[fonte]
    escala = tamanho / ttf["head"].unitsPerEm
    pen = SVGPathPen(glifos, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    for c in texto:
        if ord(c) not in cmap:
            raise ValueError(f"Glifo ausente em {fonte}: {c!r}")
        glifo = glifos[cmap[ord(c)]]
        glifo.draw(TransformPen(pen, (escala, 0, 0, -escala, x, y)))
        x += glifo.width * escala
    return pen.getCommands()


def texto(conteudo, x, y, tamanho, cor, fonte="mono", classe=None):
    atributo = f' class="{classe}"' if classe else ""
    return f'<path{atributo} fill="{cor}" d="{caminho(conteudo, x, y, tamanho, fonte)}"/>'


def trechos(partes, x, y, tamanho, fonte="mono"):
    """Escreve uma linha com vários trechos coloridos, um depois do outro."""
    saida = []
    for conteudo, cor in partes:
        if conteudo.strip():
            saida.append(texto(conteudo, x, y, tamanho, cor, fonte))
        x += largura(conteudo, fonte, tamanho)
    return "".join(saida)


def svg(largura_total, altura, titulo, corpo, estilo=""):
    style = f"<style>{estilo}</style>" if estilo else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura_total} {altura}" '
        f'width="{largura_total}" height="{altura}" role="img" aria-label="{titulo}">'
        f"<title>{titulo}</title>{style}{corpo}</svg>\n"
    )


def banner():
    W, H = 1000, 525
    fs, passo, x0 = 21, 31, 48
    char = largura("M", "mono", fs)
    y0 = 208

    consulta = [
        [("SQL> ", MUTED), ("SELECT ", BLUE), ("nome, curso, semestre, trabalho", TEXT)],
        [("  2    ", MUTED), ("FROM ", BLUE), ("devs", TEXT)],
        [("  3   ", MUTED), ("WHERE ", BLUE), ("github = ", TEXT), ("'leohssjr'", ORACLE), (";", TEXT)],
    ]
    prefixos = [5, 7, 6]

    colunas = [14, 27, 3, 18]
    cabecalho = "  ".join(n.ljust(w) for n, w in zip(["NOME", "CURSO", "SEM", "TRABALHO"], colunas))
    separador = "  ".join("-" * w for w in colunas)
    valores = ["Leonardo Sauma", "Engenharia de Software, UnB", SEMESTRE, "TCU, APEX e PL/SQL"]
    linha = "  ".join(v.ljust(w) for v, w in zip(valores, colunas))

    corpo = [
        '<defs><clipPath id="janela"><rect width="1000" height="525" rx="16"/></clipPath>'
        '<linearGradient id="brilho" x1="0" x2="1"><stop offset="0" stop-color="#066EF7"/>'
        f'<stop offset=".55" stop-color="{BLUE}"/><stop offset="1" stop-color="{ORACLE}"/>'
        "</linearGradient></defs>",
        '<g clip-path="url(#janela)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect width="{W}" height="44" fill="{PANEL}"/>',
        f'<rect y="44" width="{W}" height="2" fill="url(#brilho)"/>',
    ]
    for i, cor in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        corpo.append(f'<circle cx="{26 + i * 22}" cy="22" r="6.5" fill="{cor}"/>')
    titulo_janela = "sqlplus leohssjr@unb"
    corpo.append(texto(titulo_janela, (W - largura(titulo_janela, "mono", 15)) / 2, 27.5, 15, MUTED))
    local = "Brasília, DF"
    corpo.append(texto(local, W - 26 - largura(local, "mono", 15), 27.5, 15, MUTED))

    corpo.append(texto("Leonardo Sauma", x0 - 3, 130, 66, WHITE, "sans-bold"))
    corpo.append(f'<rect x="{x0}" y="150" width="72" height="4" rx="2" fill="{ORACLE}"/>')

    y = y0
    for i, partes in enumerate(consulta):
        inicio = x0 + prefixos[i] * char
        prompt = trechos(partes[:1], x0, y, fs)
        corpo.append(f'<g class="r p{i}">{prompt}</g>' if i else prompt)
        corpo.append(trechos(partes[1:], inicio, y, fs))
        chars = sum(len(p[0]) for p in partes) - prefixos[i]
        w = chars * char
        corpo.append(
            f'<rect class="capa c{i}" x="{inicio:.1f}" y="{y - 22}" width="{w + 4:.1f}" height="{passo}" fill="{BG}"/>'
        )
        corpo.append(
            f'<rect class="cur k{i}" x="{inicio:.1f}" y="{y - 18}" width="{char:.1f}" height="23" fill="{BLUE}"/>'
        )
        y += passo

    y += passo * 0.55
    corpo.append(f'<g class="r r0">{texto(cabecalho.rstrip(), x0, y, fs, BLUE, "mono-bold")}</g>')
    y += passo
    corpo.append(f'<g class="r r0">{texto(separador, x0, y, fs, SEPARADOR)}</g>')
    y += passo
    corpo.append(f'<g class="r r1">{texto(linha.rstrip(), x0, y, fs, WHITE)}</g>')
    y += passo * 1.55
    corpo.append(f'<g class="r r2">{texto("1 row selected.", x0, y, fs, MUTED)}</g>')
    y += passo * 1.55
    corpo.append(f'<g class="r r3">{texto("SQL>", x0, y, fs, MUTED)}')
    corpo.append(f'<rect class="fim" x="{x0 + 5 * char:.1f}" y="{y - 18}" width="{char:.1f}" height="23" fill="{BLUE}"/></g>')
    corpo.append("</g>")

    duracoes = [1.3, 0.35, 0.8]
    atrasos = [0.5, 2.0, 2.5]
    css = []
    for i, partes in enumerate(consulta):
        chars = sum(len(p[0]) for p in partes) - prefixos[i]
        w = chars * char
        css.append(
            f"@keyframes c{i}{{from{{transform:translateX(0)}}to{{transform:translateX({w + 4:.1f}px)}}}}"
            f".c{i}{{transform:translateX({w + 4:.1f}px);animation:c{i} {duracoes[i]}s steps({chars},end) {atrasos[i]}s both}}"
            f"@keyframes k{i}{{0%{{opacity:0;transform:translateX(0)}}.1%{{opacity:1;transform:translateX(0)}}"
            f"99.9%{{opacity:1;transform:translateX({w:.1f}px)}}100%{{opacity:0;transform:translateX({w:.1f}px)}}}}"
            f".k{i}{{opacity:0;animation:k{i} {duracoes[i]}s steps({chars},end) {atrasos[i]}s both}}"
        )
    css.append("@keyframes r{from{opacity:0}to{opacity:1}}.r{animation:r .01s linear both}")
    css.append(f".p1{{animation-delay:{atrasos[1]}s}}.p2{{animation-delay:{atrasos[2]}s}}")
    for i, atraso in enumerate([3.5, 3.65, 3.85, 4.05]):
        css.append(f".r{i}{{animation-delay:{atraso}s}}")
    css.append("@keyframes b{50%{opacity:0}}.fim{animation:b 1.1s steps(1,end) 4.05s infinite}")
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")

    titulo = (
        "Leonardo Sauma: consulta SQL que retorna Engenharia de Software na UnB, "
        f"{SEMESTRE} semestre, trabalho no TCU com APEX e PL/SQL"
    )
    return svg(W, H, titulo, "".join(corpo), "".join(css))


def card(projeto):
    W, H = 480, 270
    x0 = 28
    corpo = [
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="14" fill="{BG}" stroke="{LINE}" stroke-width="1.5"/>',
        texto(projeto["contexto"].upper(), x0, 42, 13, ORACLE),
        texto(projeto["nome"], x0 - 1, 84, 34, WHITE, "sans-bold"),
    ]
    seta_x, seta_y = W - 44, 30
    corpo.append(
        f'<path d="M{seta_x} {seta_y + 14}L{seta_x + 14} {seta_y}M{seta_x + 3} {seta_y}H{seta_x + 14}V{seta_y + 11}" '
        f'fill="none" stroke="{BLUE}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    y = 124
    for linha in projeto["texto"]:
        corpo.append(texto(linha, x0, y, 18, TEXT, "sans"))
        y += 26
    x = x0
    for item in projeto["stack"]:
        w = largura(item, "mono", 13) + 22
        corpo.append(f'<rect x="{x:.1f}" y="218" width="{w:.1f}" height="28" rx="7" fill="{PANEL}" stroke="{LINE}"/>')
        corpo.append(texto(item, x + 11, 236.5, 13, BLUE))
        x += w + 8
    return svg(W, H, f'{projeto["nome"]}: {" ".join(projeto["texto"])}', "".join(corpo))


def oracle():
    """APEX e PL/SQL não têm ícone no skillicons, então ganham blocos próprios."""
    W, H = 232, 48
    corpo = [
        f'<rect width="122" height="{H}" rx="10" fill="#242938"/>',
        f'<rect x="14" y="15" width="30" height="18" rx="9" fill="none" stroke="{ORACLE}" stroke-width="4.5"/>',
        texto("APEX", 54, 30.5, 19, WHITE, "mono-bold"),
        f'<rect x="130" width="102" height="{H}" rx="10" fill="#242938"/>',
        texto("PL/SQL", 144, 30.5, 19, ORACLE, "mono-bold"),
    ]
    return svg(W, H, "Oracle APEX e PL/SQL", "".join(corpo))


def contato(rotulo, cor):
    H = 44
    W = round(largura(rotulo, "mono-bold", 16)) + 76
    seta_x, seta_y = W - 28, 16
    corpo = [
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="10" fill="{BG}" stroke="{LINE}" stroke-width="1.5"/>',
        f'<circle cx="22" cy="22" r="5" fill="{cor}"/>',
        texto(rotulo, 38, 27.5, 16, WHITE, "mono-bold"),
        f'<path d="M{seta_x} {seta_y + 11}L{seta_x + 11} {seta_y}M{seta_x + 2} {seta_y}H{seta_x + 11}V{seta_y + 9}" '
        f'fill="none" stroke="{BLUE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    return svg(W, H, rotulo, "".join(corpo))


def rodape():
    W, H = 1000, 64
    corpo = [
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="12" fill="{BG}" stroke="{LINE}" stroke-width="1.5"/>',
        trechos([("SQL> ", MUTED), ("COMMIT", BLUE), (";", TEXT)], 28, 39, 19),
    ]
    aviso = "Commit complete."
    corpo.append(texto(aviso, W - 28 - largura(aviso, "mono", 19), 39, 19, MUTED))
    return svg(W, H, "SQL COMMIT; Commit complete.", "".join(corpo))


def main():
    (OUT / "hero.svg").write_text(banner(), encoding="utf-8")
    (OUT / "commit.svg").write_text(rodape(), encoding="utf-8")
    (OUT / "oracle.svg").write_text(oracle(), encoding="utf-8")
    for arquivo, (rotulo, cor) in CONTATOS.items():
        (OUT / arquivo).write_text(contato(rotulo, cor), encoding="utf-8")
    for projeto in PROJETOS:
        (OUT / projeto["arquivo"]).write_text(card(projeto), encoding="utf-8")


if __name__ == "__main__":
    main()
