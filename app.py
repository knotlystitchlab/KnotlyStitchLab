import streamlit as st
import math
import re
import plotly.graph_objects as go

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
            
            # Espaçamento muito apertado para simular tecido
            raio_base = 5 + (r_idx * 1.5) 
            altura = r_idx * 1.0          
            num_pontos = len(tokens)

            for i, t in enumerate(tokens):
                if modo_circular:
                    ang = math.radians(i * (360 / num_pontos))
                    x_c.append(raio_base * math.cos(ang))
                    y_c.append(raio_base * math.sin(ang))
                    z_c.append(altura)
                else:
                    x_c.append(i * 1.2)   
                    y_c.append(r_idx * 1.2) 
                    z_c.append(0)
                
                nomes.append(f"Carreira {r_idx+1}: {t}")
                cores.append('#6c5ce7' if t == 'sc' else '#2ecc71' if t == 'inc' else '#e74c3c')

        # Criar a visualização com "textura" de pontos grandes
        fig = go.Figure(data=[go.Scatter3d(
            x=x_c, y=y_c, z=z_c, 
            mode='markers', 
            text=nomes,
            marker=dict(
                size=10, # Pontos grandes para fechar buracos
                color=cores,
                opacity=1,
                line=dict(color='rgba(0,0,0,0.1)', width=1) # Sombra suave
            )
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_visible=False, 
                yaxis_visible=False, 
                zaxis_visible=False,
                aspectmode='data',
                bgcolor='white'
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=700
        )
        return fig

# --- LÓGICA DA INTERFACE ---
st.set_page_config(page_title="Amu Studio 3D", layout="wide")
engine = CrochetEngine()

# Gerir o estado do texto para o botão limpar funcionar
if 'receita_texto' not in st.session_state:
    st.session_state.receita_texto = "R1: 6 sc\nR2: 6 inc\nR3: [1 sc, 1 inc] x6"

def reset_receita():
    st.session_state.receita_texto = ""

st.title("🧶 Amu Studio 3D")

with st.sidebar:
    st.header("Configurações")
    modo = st.radio("Formato:", ["Circular (Amigurumi)", "Plano (Mantas)"])
    st.divider()
    if st.button("Limpar Receita"):
        reset_receita()
        st.rerun() # Força a atualização da página

# Área de texto
receita_input = st.text_area("Insira a sua receita:", value=st.session_state.receita_texto, height=150)
st.session_state.receita_texto = receita_input

if st.session_state.receita_texto:
    linhas = st.session_state.receita_texto.strip().split('\n')
    is_circular = "Circular" in modo
    
    st.subheader("Visualização com Textura 3D")
    fig_3d = engine.render_3d(linhas, is_circular)
    st.plotly_chart(fig_3d, use_container_width=True)
