import streamlit as st
import math
import re
import drawsvg as draw
import base64

class CrochetEngine:
    def parse_linha(self, linha):
        # Limpeza e normalização
        texto = linha.lower()
        texto = re.sub(r"r\d+:|c\d+:|\(\d+\)", "", texto).strip()
        
        # Tradução rápida de termos comuns
        texto = texto.replace("mr", "6 sc").replace("pb", "sc").replace("aum", "inc").replace("sc around", "18 sc")
        
        # Padrão: [sc, inc] x6
        def expand(m): return (m.group(1) + " ") * int(m.group(2))
        texto = re.sub(r"\[(.*?)\]\s*x(\d+)", expand, texto)
        
        tokens = []
        # Encontra números seguidos de tipos (ex: 6 sc)
        partes = re.findall(r'(\d+)\s*(sc|inc|dec|pb|aum|dim|v|a|\^)|(sc|inc|dec|pb|aum|dim|v|a|\^)', texto)
        
        for p in partes:
            qtd = int(p[0]) if p[0] else 1
            tipo_raw = p[1] if p[1] else p[2]
            
            if tipo_raw in ['sc', 'pb']: t = 'sc'
            elif tipo_raw in ['inc', 'aum', 'v']: t = 'inc'
            elif tipo_raw in ['dec', 'dim', 'a', '^']: t = 'dec'
            else: t = 'sc'
            tokens.extend([t] * qtd)
        return tokens

    def desenhar_simbolo(self, d, tipo, x, y, angulo):
        # Roda o símbolo para apontar para o centro
        rot = f"rotate({angulo + 90}, {x}, {y})"
        cor = "black"
        txt = "x"
        
        if tipo == 'inc': 
            txt = "v"
            cor = "#2ecc71" # Verde para aumentos
        elif tipo == 'dec': 
            txt = "A"
            cor = "#e74c3c" # Vermelho para diminuições
            
        d.append(draw.Text(txt, 16, x, y, center=True, transform=rot, fill=cor, font_weight="bold", font_family="Arial"))

    def render_circular(self, padrao):
        # Aumentamos a área de desenho para 800x800
        d = draw.Drawing(800, 800, origin='center')
        d.append(draw.Rectangle(-400, -400, 800, 800, fill='#f8f9fa')) # Fundo suave
        
        distancia_carreiras = 45 # Aproxima as carreiras
        
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            
            raio = 30 + (r_idx * distancia_carreiras)
            num_pontos = len(tokens)
            
            # Desenha uma linha guia circular (muito clara)
            d.append(draw.Circle(0, 0, raio, fill='none', stroke='#dfe6e9', stroke_width=1, stroke_dasharray="4"))
            
            for i, t in enumerate(tokens):
                # Distribuição perfeitamente circular
                ang = (i * (360 / num_pontos)) - 90
                rad = math.radians(ang)
                px = raio * math.cos(rad)
                py = raio * math.sin(rad)
                
                self.desenhar_simbolo(d, t, px, py, ang)
                
        return d

# --- INTERFACE ---
st.set_page_config(page_title="Amu Studio", page_icon="🧶", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTextArea textarea { font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.title("🧶 Amu Studio")
    st.subheader("Gerador de Diagramas")
    receita_exemplo = "R1: 6 sc\nR2: 6 inc\nR3: [1 sc, 1 inc] x6\nR4: 18 sc"
    receita = st.text_area("Insira a sua receita (exemplo):", receita_exemplo, height=300)
    st.caption("Dica: Use 'sc' para ponto baixo, 'inc' para aumento.")

with col2:
    if receita:
        engine = CrochetEngine()
        linhas = receita.strip().split('\n')
        fig = engine.render_circular(linhas)
        
        # Mostra o gráfico centrado
        st.write(fig.as_svg(), unsafe_allow_html=True)
        
        # Download
        svg_data = fig.as_svg()
        b64 = base64.b64encode(svg_data.encode()).decode()
        st.markdown(f'<a href="data:image/svg+xml;base64,{b64}" download="meu_diagrama.svg" style="display:inline-block; padding:12px 24px; background-color:#6c5ce7; color:white; text-decoration:none; border-radius:8px; font-weight:bold;">💾 Descarregar em Alta Qualidade (SVG)</a>', unsafe_allow_html=True)
