import plotly.graph_objects as go
import numpy as np

def generar_grafico_2d(coef_obj, restricciones, punto_optimo):
    fig = go.Figure()
    x1_rango = np.linspace(0, 20, 400) # Rango de visualización ajustable dinámicamente
    
    # Dibujar restricciones
    for i, rest in enumerate(restricciones):
        c1, c2 = rest['coefs']
        rhs = rest['rhs']
        
        if c2 != 0:
            x2_vals = (rhs - c1 * x1_rango) / c2
            fig.add_trace(go.Scatter(x=x1_rango, y=x2_vals, mode='lines', 
                                     name=f'Restricción {i+1}: {c1}x1 + {c2}x2 {rest["tipo"]} {rhs}'))
        else:
            # Línea vertical si c2 == 0
            fig.add_vline(x=rhs/c1, line_dash="dash", annotation_text=f'Restricción {i+1}')

    # Dibujar punto óptimo
    if punto_optimo:
        fig.add_trace(go.Scatter(x=[punto_optimo[0]], y=[punto_optimo[1]], 
                                 mode='markers', marker=dict(color='red', size=12, symbol='star'),
                                 name='Solución Óptima'))

    fig.update_layout(
        title='Método Gráfico de Resolución',
        xaxis_title='x1',
        yaxis_title='x2',
        xaxis=dict(range=[0, 20]),
        yaxis=dict(range=[0, 20]),
        hovermode="closest"
    )
    
    # Devuelve el JSON que el frontend renderizará con Plotly.js
    return fig.to_json()
