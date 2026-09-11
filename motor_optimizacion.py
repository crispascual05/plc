import pulp

def resolver_pl(tipo_opt, coef_obj, restricciones):
    """
    tipo_opt: 'max' o 'min'
    coef_obj: lista de coeficientes de la función objetivo. Ej: [3, 5]
    restricciones: lista de diccionarios. Ej: [{'coefs': [1, 0], 'tipo': '<=', 'rhs': 4}, ...]
    """
    # 1. Crear modelo
    sentido = pulp.LpMaximize if tipo_opt == 'max' else pulp.LpMinimize
    prob = pulp.LpProblem("Modelo_PL", sentido)

    # 2. Variables de decisión (asumiendo >= 0)
    n_vars = len(coef_obj)
    vars_dec = [pulp.LpVariable(f"x{i+1}", lowBound=0, cat='Continuous') for i in range(n_vars)]

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

    for name, c in prob.constraints.items():
        holgura = c.slack
        # Una restricción está saturada si su holgura es 0 (se cumple con igualdad)
        saturada = abs(holgura) < 1e-7 
        resultados["restricciones_info"].append({
            "nombre": name,
            "holgura": holgura,
            "precio_sombra": c.pi,
            "saturada": saturada
        })

    return resultados
