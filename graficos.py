import math
import plotly.graph_objects as go
import numpy as np


def _es_factible(x1, x2, restricciones, M, tol):
    # Las variables son continuas >= 0 (ver motor_optimizacion.py) y el gráfico
    # solo cubre el recuadro [0, M]x[0, M], así que ambos límites cuentan como restricciones.
    if x1 < -tol or x2 < -tol or x1 > M + tol or x2 > M + tol:
        return False
    for r in restricciones:
        c1, c2 = r['coefs']
        valor = c1 * x1 + c2 * x2
        rhs = r['rhs']
        if r['tipo'] == '<=' and valor > rhs + tol:
            return False
        if r['tipo'] == '>=' and valor < rhs - tol:
            return False
        if r['tipo'] == '=' and abs(valor - rhs) > tol:
            return False
    return True


def _calcular_vertices_region_factible(restricciones, M):
    """
    Método gráfico clásico: la región factible es un polígono convexo cuyos vértices
    están en la intersección de pares de rectas frontera (restricciones + no negatividad).
    Se prueban todas las intersecciones y se conservan las que cumplen todas las
    restricciones a la vez.
    """
    tol = 1e-6 * (1 + M)
    lineas = [(1, 0, 0), (0, 1, 0), (1, 0, M), (0, 1, M)]  # x1=0, x2=0, x1=M, x2=M
    for r in restricciones:
        lineas.append((r['coefs'][0], r['coefs'][1], r['rhs']))

    puntos = set()
    for i in range(len(lineas)):
        a1, b1, c1 = lineas[i]
        for j in range(i + 1, len(lineas)):
            a2, b2, c2 = lineas[j]
            det = a1 * b2 - a2 * b1
            if abs(det) < 1e-9:
                continue  # rectas paralelas, no se cortan
            x = (c1 * b2 - c2 * b1) / det
            y = (a1 * c2 - a2 * c1) / det
            if _es_factible(x, y, restricciones, M, tol):
                puntos.add((round(x, 6), round(y, 6)))

    if len(puntos) < 3:
        return None  # región vacía, un punto o un segmento: no hay área que rellenar

    # Ordenar los vértices alrededor del centroide para dibujar el polígono sin cruces
    cx = sum(p[0] for p in puntos) / len(puntos)
    cy = sum(p[1] for p in puntos) / len(puntos)
    return sorted(puntos, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def generar_grafico_2d(coef_obj, restricciones, punto_optimo):
    fig = go.Figure()

    # 1. Calcular límites visuales
    max_val = 10
    for rest in restricciones:
        c1, c2 = rest['coefs']
        rhs = rest['rhs']
        if c1 != 0: max_val = max(max_val, abs(rhs / c1))
        if c2 != 0: max_val = max(max_val, abs(rhs / c2))

    M = max_val * 1.3
    x_vals = np.linspace(0, M, 400)

    # 1.b Sombrear la región factible (se dibuja primero para quedar debajo de las rectas)
    vertices = _calcular_vertices_region_factible(restricciones, M)
    if vertices:
        fig.add_trace(go.Scatter(
            x=[p[0] for p in vertices] + [vertices[0][0]],
            y=[p[1] for p in vertices] + [vertices[0][1]],
            mode='lines',
            fill='toself',
            fillcolor='rgba(44, 160, 44, 0.25)',
            line=dict(width=0),
            name='Región factible',
            hoverinfo='skip'
        ))

    # 2. Dibujar las rectas de las restricciones y sus ecuaciones
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b']

    for i, rest in enumerate(restricciones):
        c1, c2 = rest['coefs']
        rhs = rest['rhs']
        
        # Corrección aplicada: La recta frontera se representa siempre como ecuación
        ecuacion_str = f"{c1}x₁ + {c2}x₂ = {rhs}"
        color = colores[i % len(colores)]
        
        if c2 != 0:
            # Rectas diagonales u horizontales
            y_vals = (rhs - c1 * x_vals) / c2
            # Se convierte a lista de Python (en vez de dejar el array de NumPy) porque
            # versiones nuevas de la librería plotly serializan arrays de NumPy en un
            # formato binario ("bdata") que el plotly.js del CDN (más antiguo) no sabe
            # leer, y la recta se queda invisible aunque los datos sean correctos.
            fig.add_trace(go.Scatter(
                x=x_vals.tolist(), y=y_vals.tolist(), mode='lines',
                line=dict(width=3, color=color),
                name=f"R{i+1}"
            ))
            
            # Anclaje de la etiqueta de texto
            x_text = M * 0.2
            y_text = (rhs - c1 * x_text) / c2
            
            if y_text < 0 or y_text > M:
                y_text = M * 0.3
                x_text = (rhs - c2 * y_text) / c1 if c1 != 0 else 0

            fig.add_annotation(
                x=x_text, y=y_text,
                text=f"<b>{ecuacion_str}</b>",
                showarrow=True, arrowhead=2, ax=40, ay=-40,
                font=dict(size=13, color=color),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor=color, borderwidth=1, borderpad=4
            )
        else:
            # Rectas puramente verticales
            x_vert = rhs / c1
            fig.add_vline(x=x_vert, line_width=3, line_color=color)
            
            fig.add_annotation(
                x=x_vert, y=M / 2,
                text=f"<b>{ecuacion_str}</b>",
                showarrow=True, arrowhead=2, ax=50, ay=0,
                font=dict(size=13, color=color),
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor=color, borderwidth=1, borderpad=4
            )

    # 3. Dibujar el Punto Óptimo
    if punto_optimo:
        fig.add_trace(go.Scatter(
            x=[punto_optimo[0]], y=[punto_optimo[1]], 
            mode='markers+text', 
            marker=dict(color='red', size=16, symbol='star'),
            text=[f"<b>ÓPTIMO ({punto_optimo[0]:.2f}, {punto_optimo[1]:.2f})</b>"],
            textposition="top right",
            textfont=dict(color='red', size=14),
            name='Solución Óptima'
        ))

    # 4. Configurar el lienzo
    fig.update_layout(
        xaxis_title='<b>Variable x₁</b>',
        yaxis_title='<b>Variable x₂</b>',
        xaxis=dict(range=[0, M], zeroline=True, zerolinewidth=3, zerolinecolor='black'),
        yaxis=dict(range=[0, M], zeroline=True, zerolinewidth=3, zerolinecolor='black'),
        showlegend=False, 
        plot_bgcolor='white',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig.to_json()
