import streamlit as st
import math
import re
import drawsvg as draw
import io
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

# --- DICIONÁRIO MULTILINGUE ---
LANGUAGES = {
    "Português (PT)": {
        "title": "🧶 Crochet Lab (Beta Aberta)",
        "shortcuts": "⌨️ Atalhos de Pontos",
        "mode": "Modo de Trabalho:",
        "circular": "Circular (Amigurumi)",
        "flat": "Plano (Mantas/Roupas)",
        "editor": "Escreve a tua receita aqui:",
        "download": "📥 Descarregar PDF Grátis (Beta)",
        "beta_info": "🛠️ Estamos em fase de testes. Reporta erros para melhorarmos!",
        "help": "Ajuda",
        "example": "Exemplo: R1: 6 pb"
    },
    "English": {
        "title": "🧶 Crochet Lab (Open Beta)",
        "shortcuts": "⌨️ Stitch Shortcuts",
        "mode": "Work Mode:",
        "circular": "Circular (Amigurumi)",
        "flat": "Flat (Blankets/Clothes)",
        "editor": "Write your pattern here:",
        "download": "📥 Download Free PDF (Beta)",
        "beta_info": "🛠️ We are in beta. Please report any bugs!",
        "help": "Help",
        "example": "Example: R1: 6 sc"
    } # Podes adicionar as outras línguas aqui conforme o dicionário anterior
}

class CrochetEngine:
    def parse_linha(self, linha):
        texto = re.sub(r"R\d+:|C\d+:|\(\d+\)", "", linha).strip().lower()
        def expand(m): return (m.group(1) + ", ") * int(m.group(2))
        texto = re.sub(r"\[(.*?)\]\s*x(\d+)", expand, texto)
        tokens = []
        partes = texto.replace(',', ' ').split()
        i = 0
        while i < len(partes):
            item = partes[i]
            if item.isdigit():
                qtd, tipo_raw, i = int(item), (partes[i+1] if i+1 < len(partes) else 'sc'), i + 2
            else: qtd, tipo_raw, i = 1, item, i + 1
            
            # Dicionário de tradução de pontos (Universal)
            if tipo_raw in ['sc', 'pb', 'p.b.', 'ms', 'fm']: t = 'sc'
            elif tipo_raw in ['inc', 'aum', 'zun', 'augm']: t = 'inc'
            elif tipo_raw in ['dec', 'dim', 'abn']: t = 'dec'
            elif tipo_raw in ['ch', 'corr', 'ml', 'lm']: t = 'ch'
            elif tipo_raw in ['slst', 'pbx', 'km', 'mc']: t = 'slst'
            elif tipo_raw in ['pa', 'dc', 'stb']: t = 'dc'
            elif tipo_raw in ['mpa', 'hdc', 'hstb']: t = 'hdc'
            else: continue
            tokens.extend([t] * qtd)
        return tokens

    def desenhar_simbolo(self, d, tipo, x, y, angulo):
        rot = f"rotate({angulo + 90}, {x}, {y})"
        if tipo == 'sc': d.append(draw.Text('x', 12, x, y, center=True, transform=rot))
        elif tipo == 'inc': d.append(draw.Text('v', 12, x, y, center=True, fill='green', transform=rot))
        elif tipo == 'dec': d.append(draw.Text('^', 12, x, y, center=True, fill='red', transform=rot))
        elif tipo == 'ch': d.append(draw.Ellipse(x, y, 3, 5, fill='none', stroke='black', transform=rot))
        elif tipo == 'slst': d.append(draw.Circle(x, y, 2, fill='black'))
        elif tipo in ['dc', 'hdc']:
            d.append(draw.Lines(x-5, y-10, x+5, y-10, x, y-10, x, y+5, stroke='black', stroke_width=1.2, transform=rot))
            if tipo == 'dc': d.append(draw.Line(x-3, y-2, x+3, y-4, stroke='black', transform=rot))

    def render_circular(self, padrao):
        d = draw.Drawing(800, 800, origin='center')
        d.append(draw.Rectangle(-400, -400, 800, 800, fill='white'))
        camada_ant = []
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            raio, nova_camada = 50 + (r_idx * 45), []
            if r_idx == 0:
                step = 360 / len(tokens)
                for i, t in enumerate(tokens): nova_camada.append({'ang': i*step, 'tipo': t})
            else:
                ptr = 0
                for t in tokens:
                    pai = camada_ant[ptr % len(camada_ant)]
                    if t == 'inc':
                        nova_camada.extend([{'ang': pai['ang']-5, 'tipo': t}, {'ang': pai['ang']+5, 'tipo': t}]); ptr += 1
                    elif t == 'dec' and (ptr+1) < len(camada_ant):
                        pai2 = camada_ant[ptr+1]; nova_camada.append({'ang': (pai['ang']+pai2['ang'])/2, 'tipo': t}); ptr += 2
                    else:
                        nova_camada.append({'ang': pai['ang'], 'tipo': t}); ptr += 1
            for p in nova_camada:
                rad = math.radians(p['ang'])
                self.desenhar_simbolo(d, p['tipo'], raio*math.cos(rad), raio*math.sin(rad), p['ang'])
            camada_ant = nova_camada
        return d

    def render_flat(self, padrao):
        d = draw.Drawing(1000, 800); d.append(draw.Rectangle(0, 0, 1000, 800, fill='white'))
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if r_idx % 2 != 0: tokens = tokens[::-1]
            y = 700 - (r_idx * 50)
            for c_idx, t in enumerate(tokens):
                self.desenhar_simbolo(d, t, 60 + (c_idx*35), y, angulo=-90)
        return d

# --- APP STREAMLIT ---
engine = CrochetEngine()
if 'texto' not in st.session_state: st.session_state.texto = ""

with st.sidebar:
    lang = st.selectbox("🌐 Language", list(LANGUAGES.keys()))
    t = LANGUAGES[lang]
    st.header(t["shortcuts"])
    c1, c2 = st.columns(2)
    pts = [("Pb", "pb"), ("Pa", "pa"), ("Aum", "inc"), ("Dim", "dec"), ("Corr", "ch"), ("Pbx", "slst")]
    for i, (n, s) in enumerate(pts):
        if (c1 if i%2==0 else c2).button(n): st.session_state.texto += f" {s},"
    st.divider()
    modo = st.radio(t["mode"], [t["circular"], t["flat"]])
    st.warning(t["beta_info"])

st.title(t["title"])
receita = st.text_area(t["editor"], value=st.session_state.texto, height=250)
st.session_state.texto = receita

if receita:
    linhas = receita.strip().split('\n')
    fig = engine.render_circular(linhas) if modo == t["circular"] else engine.render_flat(linhas)
    st.write(fig.as_svg(), unsafe_allow_html=True)
    
    # DOWNLOAD GRATUITO EM BETA
    svg_io = io.BytesIO(fig.as_svg().encode('utf-8'))
    drawing_rl = svg2rlg(svg_io)
    pdf_io = io.BytesIO()
    renderPDF.drawToFile(drawing_rl, pdf_io)
    st.download_button(t["download"], pdf_io.getvalue(), "pattern_beta.pdf")