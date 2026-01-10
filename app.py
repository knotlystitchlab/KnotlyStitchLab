import streamlit as st
import math
import re
import drawsvg as draw
import base64
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
            if tipo_raw in ['sc']: t = 'sc'
            elif tipo_raw in ['inc', 'v']: t = 'inc'
            elif tipo_raw in ['dec', 'a', '^']: t = 'dec'
            elif tipo_raw in ['ch', 'corr']: t = 'ch'
            else: t = 'sc'
            tokens.extend([t] * qtd)
        return tokens

    def desenhar_simbolo_2d(self, d, tipo, x, y, angulo):
        rot = f"rotate({angulo}, {x}, {y})"
        if tipo == 'sc': d.append(draw.Text('x', 16, x, y, center=True, transform=rot))
        elif tipo == 'inc': d.append(draw.Text('v', 16, x, y, center=True, fill='#2ecc71', transform=rot))
        elif tipo == 'dec': d.append(draw.Text('A', 16, x, y, center=True, fill='#e74c3c', transform=rot))
        elif tipo == 'ch': d.append(draw.Circle(x, y, 3, fill='none', stroke='black'))

    def render_circular_2d(self, padrao):
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
                self.desenhar_simbolo_2d(d, t, raio*math.cos(rad), raio*math.sin(rad), ang+90)
        return d

    def render_flat_2d(self, padrao):
        d = draw.Drawing(800, 500)
        d.append(draw.Rectangle(0, 0, 800, 500, fill='white'))
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            if r_idx % 2 != 0: tokens = tokens[::-1]
            y = 400 - (r_idx * 40)
            for c_idx, t in enumerate(tokens):
                x = 50 + (c_idx * 30)
                self.desenhar_simbolo_2d(d, t, x, y, 0)
        return d

    def render_3d(self, padrao, modo_circular):
        x_c, y_c, z_c, cores, nomes = [], [], [], [], []
        
        for r_idx, linha in enumerate(padrao):
            tokens = self.parse_linha(linha)
            if not tokens: continue
            
            for i, t in enumerate(tokens):
                if modo_circular:
                    raio = 20 + (r_idx * 10)
                    ang = math.radians(i * (360 / len(tokens)))
                    x_c.append(raio * math.cos(ang))
                    y_c.append(raio * math.sin(ang))
                    z_c.append(r_idx * 5)
                else:
                    x_c.append(i * 10)
                    y_c.append(r_idx * 10)
                    z_c.append(0)
                
                nomes.append(f"Carreira {r_idx+1}: {t}")
                cores.append('#6c5ce7' if t == 'sc' else '#2ecc71' if t == 'inc' else '#e74c3c')

        fig = go.Figure(data=[go.Scatter3d(
            x=x_c, y=y_c, z=z_c, mode='markers',
            text=nomes
