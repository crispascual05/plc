import plotly.graph_objects as go
import numpy as np
import itertools
from scipy.spatial import ConvexHull

def generar_grafico_2d(coef_obj, restricciones, punto_optimo):
    fig = go.Figure()
    
    # 1. Determinar el límite visual del gráfico (M) para evitar áreas infinitas
    max_interseccion = 10
    for rest in restricciones:
        c1, c2 = rest['coefs']
        rhs = rest['rhs']
        if c1 != 0: max_interseccion = max(max_interseccion, abs(rhs / c1))
        if c2 != 0: max_interseccion = max(max_interseccion, abs(rhs / c2))
    
    M = max_interseccion * 1.25 # Margen del 25% para que la gráfica respire

    # 2. Recopilar ecuaciones de las rectas (Restricciones + Ejes + Límites visuales)
    rectas = [(r['coefs'][0], r['coefs'][1], r['rhs']) for r in restricciones]
    rectas.append((1, 0, 0)) # x1 = 0 (Eje Y)
    rectas.append((0, 1, 0)) # x2 = 0 (Eje X)
    rectas.append((1, 0, M)) # Límite derecho artificial
    rectas.append((0, 1, M)) # Límite superior artificial

    # 3. Calcular todas las intersecciones posibles (vértices candidatos)
    puntos = []
    for (A1, B1, C1), (A2, B2, C2) in itertools.combinations(rectas, 2):
        det = A1 * B2 - A2 * B1
        if abs(det) > 1e-9: # Si las líneas no son paralelas
            x1 = (C1 * B2 - C2 * B1) / det
            x2 = (A1 * C2 - A2 * C1) / det
            puntos.append((x1, x2))

    # 4. Filtrar puntos: quedarse solo con los que cumplen todas las restricciones
    puntos_validos = []
    for x1, x2 in puntos:
        # Descartar fuera del cuadrante positivo o del límite M
        if round(x1, 5) < 0 or round(x2, 5) < 0 or round(x1, 5) > M or round(x2, 5) > M:
            continue
            
        es_valido = True
        for r in restricciones:
            c1, c2 = r['coefs']
            valor = c1 * x1 + c2 * x2
            rhs = r['rhs']
            
            # Tolerancia 1e-5 por problemas de precisión de coma flotante
            if r['tipo'] == '<=' and round(valor - rhs, 5) > 0:
                es_valido = False; break
            elif r['tipo'] == '>=' and round(valor - rhs, 5) < 0:
                es_valido = False; break
            elif r['tipo'] == '=' and abs(valor - rhs) > 1e-5:
                es_valido = False; break
                
        if es_valido:
            if not any(np.allclose([x1, x2], p, atol=1e-4) for p in puntos_validos):
                puntos_validos.append((x1, x2))

    # 5. Dibujar el polígono del Área Factible
    if len(puntos_validos) >= 3:
        puntos_arr = np.array(puntos_validos)
        hull = ConvexHull(puntos_arr) # Ordena los vértices geométricamente
        puntos_borde = puntos_arr[hull.vertices]
        
        # Cerrar el polígono
        x_hull = np.append(puntos_borde[:, 0], puntos_borde[0, 0])
        y_hull = np.append(puntos_borde[:, 1], puntos_borde[0, 1])
        
        fig.add_trace(go.Scatter(
            x=x_hull, y=y_hull, fill='toself', mode='lines',
            fillcolor='rgba(40, 167, 69, 0.3)', # Verde semitransparente
            line=dict(color='rgba(255,255,255,0)'),
            name='Área Factible'
        ))

    # 6. Dibujar las rectas de las restricciones (extendidas por el gráfico)
    x1_rango = np.linspace(0, M, 400)
    for i, rest in enumerate(restricciones):
        c1, c2 = rest['coefs']
        rhs = rest['rhs']
        
        if c2 != 0:
            x2_vals = (rhs - c1 * x1_rango) / c2
            # Recortar visualmente la recta para que no deforme el autoscale
            x1_filtrado = x1_rango[(x2_vals >= -1) & (x2_vals <= M + 1)]
            x2_filtrado = x2_vals[(x2_vals >= -1) & (x2_vals <= M + 1)]
            
            fig.add_trace(go.Scatter(x=x1_filtrado, y=x2_filtrado, mode='lines', 
                                     line=dict(width=2.5),
                                     name=f'R{i+1}: {c1}x₁ + {c2}x₂ {rest["tipo"]} {rhs}'))
        else:
            fig.add_vline(x=rhs/c1, line=dict(color="black", width=2, dash="dot"), name=f'R{i+1}')

    # 7. Dibujar la solución óptima
    if punto_optimo:
        fig.add_trace(go.Scatter(
            x=[punto_optimo[0]], y=[punto_optimo[1]], 
            mode='markers', 
            marker=dict(color='red', size=16, symbol='star', line=dict(color='darkred', width=1)),
            name='Solución Óptima'
        ))

    fig.update_layout(
        title='Resolución Gráfica del Modelo',
        xaxis_title='x₁',
        yaxis_title='x₂',
        xaxis=dict(range=[0, M], zeroline=True, zerolinewidth=3, zerolinecolor='black'),
        yaxis=dict(range=[0, M], zeroline=True, zerolinewidth=3, zerolinecolor='black'),
        hovermode="closest",
        plot_bgcolor='white', # Fondo limpio para que destaque el área verde
    )
    
    return fig.to_json()
