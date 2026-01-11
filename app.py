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
            
            # Compactação máxima para parecer tecido
            raio_base = 5 + (r_idx * 1.8) 
            altura = r_idx * 1.2          
            num_pontos = len(tokens)

            for i, t in enumerate(tokens):
                if modo_circular:
                    ang = math.radians(i * (360 / num_pontos))
                    x_c.append(raio_base * math.cos(ang))
                    y_c.append(raio_base * math.sin(ang))
                    z_c.append(altura)
                else:
                    x_c.append(i * 1.5)   
                    y_c.append(r_idx * 1.5) 
                    z_c.append(0)
                
                nomes.append(f"Carreira {r_idx+1}: {t}")
                # Cores com variação para simular textura (brilho/sombra)
                base_color = '#6c5ce7' if t == 'sc' else '#2ecc71' if t == 'inc' else '#e74c3c'
                cores.append(base_color)

        # Usamos Scatter3d com definições de luz e sombra
        fig = go.Figure(data=[go.Scatter3d(
            x=x_c, y=y_c, z=z_c, 
            mode='markers', 
            text=nomes,
            marker=dict(
                size=8, # Pontos maiores para "fechar" os buracos
                color=cores,
                opacity=1,
                # Adiciona uma linha de contorno suave para dar volume
                line=dict(color='rgba(50, 50, 50, 0.2)', width=1),
                # Simula brilho alterando o símbolo
                symbol='circle' 
            )
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_visible=False, 
                yaxis_visible=False, 
                zaxis_visible=False, # Remove os eixos para focar na "peça"
                aspectmode='data',
                # Fundo cinza muito claro para realçar a textura
                bgcolor='white'
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=700
        )
        return fig
# --- INTERFACE ---
st.set_page_config(page_title="Amu Studio 3D", layout="wide")
engine = CrochetEngine()

# Lógica para limpar a receita
if 'receita_input' not in st.session_state:
    st.session_state.receita_input = "R1: 6 sc\nR2: 6 inc\nR3: [1 sc, 1 inc] x6"

def limpar_texto():
    st.session_state.receita_input = ""

st.title("🧶 Amu Studio 3D")

with st.sidebar:
    st.header("Configurações")
    modo = st.radio("Formato:", ["Circular (Amigurumi)", "Plano (Mantas)"])
    st.divider()
    # Botão de Limpar
    st.button("Limpar Receita", on_click=limpar_texto)
    st.info("Dica: Usa o rato para rodar e o scroll para fazer zoom no modelo.")

# Input de texto vinculado ao session_state
receita = st.text_area("Insira a sua receita:", value=st.session_state.receita_input, key="receita_field", height=150)
# Atualiza o estado para manter sincronizado
st.session_state.receita_input = receita

if receita:
    linhas = receita.strip().split('\n')
    is_circular = "Circular" in modo
    
    st.subheader("Visualização 3D")
    fig_3d = engine.render_3d(linhas, is_circular)
    st.plotly_chart(fig_3d, use_container_width=True)

