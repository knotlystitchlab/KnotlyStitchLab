import streamlit as st
import math
import re
import drawsvg as draw
import base64

class CrochetEngine:
    def parse_linha(self, linha):
        texto = linha.lower()
        texto = re.sub(r"r\d+:|c\d+:|\(\d+\)", "", texto).strip()
        texto = texto.replace("pb", "sc").replace("aum", "inc").replace("dim", "dec")
        
        def expand(m): return (m.group(1) + " ") * int(m.group(2))
        texto = re.sub(r"\[(.*?)\]\s*x(\d+)", expand, texto)
        
        tokens = []
        partes = re.findall(r'(\d+)\s*(sc|inc|dec|v|a|\^|ch|corr)|(sc|inc|dec|v|a|\^|ch|corr)', texto)
        for p in partes:
            qtd = int(p[0]) if p[0] else 1
            tipo_raw = p[1] if p[1] else p[2]
            if tipo_raw in ['sc']: t = 'sc'
            elif tipo_raw in ['inc', 'v']: t = 'inc'
            elif tipo_raw in ['dec', 'a', '^']: t = 'dec'
            elif tipo_raw in ['ch', 'corr']: t = 'ch'
            else: t = 'sc'
            tokens.extend([t] * qtd)
        return tokens

    def desenhar_simbolo(self, d, tipo, x, y, angulo):
        rot = f"rotate({angulo}, {x}, {y})"
        if tipo == 'sc': d.append(draw.Text('x', 16, x, y, center=True, transform=rot))
        elif tipo == 'inc': d.append(draw.Text('v', 16, x, y, center=True, fill='#2ecc71', transform=rot))
        elif tipo == 'dec': d.append(draw.Text('A', 16, x, y, center=True, fill='#e74c3c', transform=rot))
        elif tipo == 'ch': d.append(draw.Circle(x, y, 3, fill='none', stroke='black'))

    def render_circular(self, padrao):
        d = draw.Drawing(600, 600, origin='center')
        d.append(draw.Rectangle(-300, -300, 600, 600, fill='white'))
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            raio = 40 + (r_idx * 40)
            step = 360 / len(tokens)
            for i, t in enumerate(tokens):
                ang = (i * step) - 90
                rad = math.radians(ang)
                self.desenhar_simbolo(d, t, raio*math.cos(rad), raio*math.sin(rad), ang+90)
        return d

    def render_flat(self, padrao):
        # Desenho retangular para mantas
        d = draw.Drawing(800, 500)
        d.append(draw.Rectangle(0, 0, 800, 500, fill='white'))
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            # Alterna a direção da carreira (ida e volta)
            if r_idx % 2 != 0: tokens = tokens[::-1]
            
            y = 400 - (r_idx * 40)
            for c_idx, t in enumerate(tokens):
                x = 50 + (c_idx * 30)
                self.desenhar_simbolo(d, t, x, y, 0)
        return d

# --- INTERFACE ---
st.set_page_config(page_title="Amu Studio", layout="wide")

with st.sidebar:
    st.title("🧶 Configurações")
    modo = st.radio("Modo de Trabalho:", ["Circular (Amigurumi)", "Plano (Mantas/Flats)"])
    st.divider()
    st.info("O modo Plano organiza os pontos em linhas horizontais.")

st.title("🧶 Amu Studio - Design de Padrões")
receita = st.text_area("Insira a receita por carreiras:", "R1: 6 sc\nR2: 6 sc", height=200)

if receita:
    engine = CrochetEngine()
    linhas = receita.strip().split('\n')
    
    if "Circular" in modo:
        fig = engine.render_circular(linhas)
    else:
        fig = engine.render_flat(linhas)
    
    st.write(fig.as_svg(), unsafe_allow_html=True)
    
    # Download
    svg_data = fig.as_svg()
    b64 = base64.b64encode(svg_data.encode()).decode()
    st.markdown(f'<a href="data:image/svg+xml;base64,{b64}" download="diagrama.svg" style="padding:10px; background-color:#6c5ce7; color:white; text-decoration:none; border-radius:5px;">📥 Descarregar SVG</a>', unsafe_allow_html=True)
