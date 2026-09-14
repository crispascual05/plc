import pulp

def resolver_pl(tipo_opt, coef_obj, restricciones, no_negatividad=True):
    """
    tipo_opt: 'max' o 'min'
    coef_obj: lista de coeficientes de la función objetivo. Ej: [3, 5]
    restricciones: lista de diccionarios. Ej: [{'coefs': [1, 0], 'tipo': '<=', 'rhs': 4}, ...]
    no_negatividad: booleano que indica si x >= 0
    """
    # 1. Crear modelo
    sentido = pulp.LpMaximize if tipo_opt == 'max' else pulp.LpMinimize
    prob = pulp.LpProblem("Modelo_PL", sentido)

    # 2. Variables de decisión
    n_vars = len(coef_obj)
    limite_inferior = 0 if no_negatividad else None
    vars_dec = [pulp.LpVariable(f"x{i+1}", lowBound=limite_inferior, cat='Continuous') for i in range(n_vars)]

    # 3. Función Objetivo
    prob += pulp.lpSum([coef_obj[i] * vars_dec[i] for i in range(n_vars)]), "Z"

    # 4. Restricciones dinámicas
    for i, rest in enumerate(restricciones):
        expr = pulp.lpSum([rest['coefs'][j] * vars_dec[j] for j in range(n_vars)])
        if rest['tipo'] == '<=':
            prob += (expr <= rest['rhs'], f"Restriccion_{i+1}")
        elif rest['tipo'] == '>=':
            prob += (expr >= rest['rhs'], f"Restriccion_{i+1}")
        elif rest['tipo'] == '=':
            prob += (expr == rest['rhs'], f"Restriccion_{i+1}")

    # 5. Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    estado = pulp.LpStatus[prob.status]

    if estado != 'Optimal':
        return {"estado": estado}

    # 6. Extraer resultados y saturación
    resultados = {
        "estado": estado,
        "z_optima": pulp.value(prob.objective),
        "variables": {v.name: v.varValue for v in prob.variables()},
        "restricciones_info": []
    }

    for i, rest in enumerate(restricciones):
        nombre = f"Restriccion_{i+1}"
        c = prob.constraints[nombre]
        
        holgura = c.slack if rest['tipo'] != '>=' else -c.slack
        saturada = abs(holgura) < 1e-7
        
        resultados["restricciones_info"].append({
            "nombre": nombre,
            "tipo": rest['tipo'],
            "holgura": abs(holgura),
            "precio_sombra": c.pi,
            "saturada": saturada
        })

    return resultados
