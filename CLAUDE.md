# Perfil: Estudiante de Ingeniería en Organización Industrial

## Contexto del proyecto
Aplicación web para resolver problemas de Programación Lineal (PL) como parte de mis estudios.
- Backend: Flask (`app.py`) expone una API (`/api/resolver`) que recibe función objetivo y restricciones en JSON.
- Motor de optimización: `motor_optimizacion.py`, usando PuLP (CBC) para resolver el modelo (max/min, variables continuas ≥ 0).
- Visualización: `graficos.py` genera gráficos 2D (Plotly) de la región factible y el punto óptimo cuando hay 2 variables.
- Frontend: plantillas en `templates/` (HTML servido con `render_template`).

## Mi perfil
- Estudio Ingeniería en Organización Industrial; conozco la teoría de PL (método símplex, dualidad, precios sombra, holguras) pero soy más nuevo en desarrollo web/Python de nivel profesional.
- Prefiero explicaciones que conecten el código con los conceptos de Investigación Operativa (ej. relacionar `c.slack` y `c.pi` con holgura y precio sombra).

## Cómo quiero que trabajes conmigo
- Explica el porqué de los cambios, no solo el qué, especialmente cuando toques la lógica matemática/de optimización.
- Si detectas errores conceptuales de PL (ej. tipos de restricción, variables no acotadas, casos no factibles/no acotados), señálalos explícitamente.
- Código simple y directo: es un proyecto académico/pequeño, evita sobre-ingeniería o abstracciones innecesarias.
- Al modificar `motor_optimizacion.py` o `graficos.py`, ten en cuenta que de momento solo soporta variables continuas y (en el gráfico) máximo 2 variables de decisión.

## Stack técnico
- Python 3, Flask, PuLP (CBC), Plotly, NumPy, SciPy.
- Sin tests automatizados todavía (si añades funcionalidad crítica, sugiere tests).
