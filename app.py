from flask import Flask, request, jsonify, render_template
import json

from motor_optimizacion import resolver_pl
from graficos import generar_grafico_2d

app = Flask(__name__)

# Esta ruta sirve la interfaz web (el HTML)
@app.route('/')
def index():
    return render_template('index.html')

# Esta ruta resuelve las matemáticas (la API)
@app.route('/api/resolver', methods=['POST'])
def resolver_modelo():
    datos = request.json
    tipo_opt = datos.get('tipo', 'max')
    coef_obj = datos.get('coef_obj', [])
    restricciones = datos.get('restricciones', [])
    no_neg = datos.get('no_negatividad', True) # Extraemos la nueva variable
    
    # Pasamos el parámetro de no negatividad al motor matemático
    solucion = resolver_pl(tipo_opt, coef_obj, restricciones, no_neg)
    respuesta = {"solucion": solucion}

    if len(coef_obj) == 2 and solucion.get('estado') == 'Optimal':
        punto_optimo = [solucion['variables']['x1'], solucion['variables']['x2']]
        # Le pasamos la condición al gráfico para que ajuste los cuadrantes
        grafico_json = generar_grafico_2d(coef_obj, restricciones, punto_optimo, no_neg)
        respuesta["grafico"] = json.loads(grafico_json)
        
    return jsonify(respuesta)

if __name__ == '__main__':
    # Usar debug=True es vital ahora mismo para ver los fallos en rojo
    app.run(debug=True)
