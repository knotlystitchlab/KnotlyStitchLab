import streamlit as st
import math
import re
import drawsvg as draw
import base64

# --- ENGINE DE CROCHET SIMPLIFICADA (SEM CAIRO) ---
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
            
            if tipo_raw in ['sc', 'pb', 'p.b.']: t = 'sc'
            elif tipo_raw in ['inc', 'aum', 'v']: t = 'inc'
            elif tipo_raw in ['dec', 'dim', '^']: t = 'dec'
            elif tipo_raw in ['ch', 'corr']: t = 'ch'
            else: t = 'sc'
            tokens.extend([t] * qtd)
        return tokens

    def desenhar_simbolo(self, d, tipo, x, y, angulo):
        rot = f"rotate({angulo + 90}, {x}, {y})"
        if tipo == 'sc': d.append(draw.Text('x', 14, x, y, center=True, transform=rot))
        elif tipo == 'inc': d.append(draw.Text('v', 14, x, y, center=True, fill='green', transform=rot))
        elif tipo == 'dec': d.append(draw.Text('A', 14, x, y, center=True, fill='red', transform=rot))
        elif tipo == 'ch': d.append(draw.Circle(x, y, 3, fill='none', stroke='black'))

    def render_circular(self, padrao):
        d = draw.Drawing(600, 600, origin='center')
        d.append(draw.Rectangle(-300, -300, 600, 600, fill='white'))
        camada_ant = []
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            raio, nova_camada = 40 + (r_idx * 35), []
            step = 360 / len(tokens)
            for i, t in enumerate(tokens):
                ang = i * step
                rad = math.radians(ang)
                self.desenhar_simbolo(d, t, raio*math.cos(rad), raio*math.sin(rad), ang)
                nova_camada.append({'ang': ang})
            camada_ant = nova_camada
        return d

# --- INTERFACE ---
st.set_page_config(page_title="Amu Studio Beta", page_icon="🧶")
st.title("🧶 Amu Studio (Versão Beta)")

engine = CrochetEngine()
receita = st.text_area("Cole a sua receita aqui:", "R1: 6 pb\nR2: 6 aum", height=200)

if receita:
    linhas = receita.strip().split('\n')
    fig = engine.render_circular(linhas)
    
    # Mostrar o Gráfico
    st.write(fig.as_svg(), unsafe_allow_html=True)
    
    # Botão de Download Simples (SVG)
    svg_data = fig.as_svg()
    b64 = base64.b64encode(svg_data.encode()).decode()
    href = f'<a href="data:image/svg+xml;base64,{b64}" download="diagrama.svg" style="padding:10px; background-color:green; color:white; text-decoration:none; border-radius:5px;">📥 Descarregar Gráfico (SVG)</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.info("Nota: Em Beta, o download é em formato SVG (abre em qualquer navegador ou Word).")
