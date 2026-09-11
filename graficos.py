import plotly.graph_objects as go
import numpy as np

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
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_vals, mode='lines', 
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
