import streamlit as st
import math
import re
import plotly.graph_objects as go

class CrochetEngine:
    def parse_linha(self, linha):
        # Limpeza básica da linha
        texto = linha.lower()
        texto = re.sub(r"r\d+:|c\d+:|\(\d+\)", "", texto).strip()
        texto = texto.replace("pb", "sc").replace("aum", "inc").replace("dim", "dec")
        
        # Expandir padrões como [sc, inc] x6
        def expand(m): return (m.group(1) + " ") * int(m.group(2))
        texto = re.sub(r"\[(.*?)\]\s*x(\d+)", expand, texto)
        
        tokens = []
        partes = re.findall(r'(\d+)\s*(sc|inc|dec|v|a|\^|ch|corr)|(sc|inc|dec|v|a|\^|ch|corr)', texto)
        for p in partes:
            qtd = int(p[0]) if p[0] else 1
            tipo_raw = p[1] if p[1] else p[2]
            t = 'sc'
            if tipo_raw in ['inc', 'v']: t = 'inc'
            elif tipo_raw in ['dec', 'a', '^']: t = 'dec'
            elif tipo_raw in ['ch', 'corr']: t = 'ch'
            tokens.extend([t] * qtd)
        return tokens

def render_3d(self, padrao, modo_circular):
        x_c, y_c, z_c, cores, nomes = [], [], [], [], []
        
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            
            # Valores ajustados para menor espaçamento
            raio_base = 10 + (r_idx * 4) # Crescimento de raio mais suave
            altura = r_idx * 2          # Subida de carreira mais curta
            
            num_pontos = len(tokens)
            for i, t in enumerate(tokens):
                if modo_circular:
                    ang = math.radians(i * (360 / num_pontos))
                    x_c.append(raio_base * math.cos(ang))
                    y_c.append(raio_base * math.sin(ang))
                    z_c.append(altura)
                else:
                    x_c.append(i * 5)   # Pontos mais próximos horizontalmente
                    y_c.append(r_idx * 5) # Carreiras mais próximas
                    z_c.append(0)
                
                nomes.append(f"Carreira {r_idx+1}: {t}")
                cores.append('#6c5ce7' if t == 'sc' else '#2ecc71' if t == 'inc' else '#e74c3c')

        fig = go.Figure(data=[go.Scatter3d(
            x=x_c, y=y_c, z=z_c, 
            mode='markers+lines' if len(x_c) < 500 else 'markers',
            text=nomes,
            marker=dict(size=6, color=cores, opacity=0.9, line=dict(width=0))
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_visible=False, 
                yaxis_visible=False, 
                zaxis_visible=True,
                aspectmode='data' # Isto obriga o 3D a respeitar as proporções reais
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )
        return fig

# --- INTERFACE ---
st.set_page_config(page_title="Amu Studio 3D", layout="wide")
engine = CrochetEngine()

with st.sidebar:
    st.title("🧶 Configurações")
    modo = st.radio("Formato do Trabalho:", ["Circular (Amigurumi)", "Plano (Mantas)"])
    st.divider()
    st.markdown("### Legenda 3D:")
    st.markdown("🔵 Ponto Baixo (sc)")
    st.markdown("🟢 Aumento (inc)")
    st.markdown("🔴 Diminuição (dec)")

st.title("🧶 Amu Studio 3D")
receita = st.text_area("Insira a sua receita:", "R1: 6 sc\nR2: 6 inc\nR3: [1 sc, 1 inc] x6", height=150)

if receita:
    linhas = receita.strip().split('\n')
    is_circular = "Circular" in modo
    
    st.subheader("Visualização Interativa 3D")
    st.info("Podes clicar e arrastar a imagem abaixo para rodar o modelo!")
    
    fig_3d = engine.render_3d(linhas, is_circular)
    st.plotly_chart(fig_3d, use_container_width=True)

