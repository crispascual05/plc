from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/resolver', methods=['POST'])
def resolver_modelo():
    datos = request.json
    tipo_opt = datos.get('tipo', 'max')
    coef_obj = datos.get('coef_obj', [])
    restricciones = datos.get('restricciones', [])
    
    # 1. Resolver numéricamente
    solucion = resolver_pl(tipo_opt, coef_obj, restricciones)
    
    respuesta = {"solucion": solucion}

    # 2. Si son 2 variables y hay solución óptima, generar gráfico
    if len(coef_obj) == 2 and solucion.get('estado') == 'Optimal':
        punto_optimo = [solucion['variables']['x1'], solucion['variables']['x2']]
        grafico_json = generar_grafico_2d(coef_obj, restricciones, punto_optimo)
        respuesta["grafico"] = json.loads(grafico_json)
        
    return jsonify(respuesta)
