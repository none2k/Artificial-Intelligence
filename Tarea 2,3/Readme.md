# Tarea 2.3 — Visualización de Búsqueda A* (Opción A)

**Alumno:** Miguel Puente Flores  
**Matrícula:** 1998334  
**Facultad:** Facultad de Ciencias Físico Matemáticas (FCFM)  
**Fecha:** 22 de noviembre de 2026  

**Enlace al video demostrativo:** https://drive.google.com/file/d/1QWqoaeXa0lB9MeyCMPWdK7KpumKvkLkQ/view?usp=sharing

---

## Descripción del Proyecto

Este proyecto implementa y visualiza de manera interactiva el algoritmo de búsqueda informada **A\*** sobre una cuadrícula 2D con obstáculos, resolviendo el problema clásico de búsqueda de ruta más corta (*pathfinding*), aplicable a escenarios como navegación de robots en almacenes, cálculo de rutas en mapas urbanos o inteligencia artificial en videojuegos.

Para evidenciar las ventajas de utilizar una heurística frente a una búsqueda no informada, el repositorio incluye además una visualización del **Algoritmo de Dijkstra** con exactamente la misma interfaz y esquema de colores.

### Archivos incluidos
* `astar_visual.py`: Implementación y visualización interactiva del algoritmo A\*.
* `dijkstra_visual.py`: Implementación y visualización interactiva del algoritmo de Dijkstra para comparación directa.

---

## Requisitos e Instalación

El proyecto fue desarrollado en **Python 3** utilizando la librería gráfica `pygame-ce` (Pygame Community Edition) para renderizar la cuadrícula y animar el proceso interno de exploración en tiempo real.

Para instalar la dependencia necesaria, ejecuta el siguiente comando en tu terminal:

```bash
pip install pygame-ce
```

---

## Ejecución y Controles

Clona o descarga el repositorio, navega a la carpeta del proyecto desde tu terminal y ejecuta cualquiera de los dos programas:

```bash
# Para ejecutar la visualización de A*
python astar_visual.py

# Para ejecutar la visualización comparativa de Dijkstra
python dijkstra_visual.py
```

### Controles interactivos
* **Clic izquierdo:** Coloca el nodo de inicio (primer clic), el nodo meta (segundo clic) y dibuja obstáculos (clics siguientes o arrastrando).
* **Clic derecho:** Borra cualquier celda (inicio, meta u obstáculo).
* **Barra espaciadora (`Espacio`):** Inicia la animación del algoritmo.
* **Tecla `C`:** Limpia todo el tablero para configurar un nuevo escenario.

### Leyenda de colores
| Color | Significado |
| :--- | :--- |
| **Amarillo** | Nodo de inicio |
| **Morado** | Nodo meta (objetivo) |
| **Negro** | Obstáculo (celda intransitable) |
| **Verde** | Frontera de búsqueda (*Open Set* — nodos en la cola de prioridad) |
| **Rojo** | Nodos ya explorados (*Closed Set*) |
| **Azul** | Camino óptimo reconstruido |
| **Blanco** | Nodo no visitado |

---

## Decisiones de Diseño y Justificación Técnica

### 1. Estructura de datos y función de costo
Para gestionar la frontera de búsqueda (*Open Set*) de manera eficiente, se utiliza una **Cola de Prioridad** (`PriorityQueue`, implementada internamente como un *Min-Heap*). En cada iteración, el algoritmo extrae el nodo $n$ con el menor valor de la función de evaluación:

$$f(n) = g(n) + h(n)$$

Donde:
* $g(n)$ es el costo real acumulado desde el nodo de inicio hasta el nodo actual $n$ (cada movimiento ortogonal tiene un costo de $1$).
* $h(n)$ es el costo estimado por la heurística desde el nodo $n$ hasta la meta.
* $f(n)$ es el costo total estimado de la ruta que pasa por $n$.

### 2. Elección y admisibilidad de la heurística
Se eligió la **Distancia Manhattan** como función heurística:

$$h(p_1, p_2) = |x_1 - x_2| + |y_1 - y_2|$$

**¿Por qué es admisible?**  
En esta cuadrícula solo se permiten desplazamientos ortogonales (arriba, abajo, izquierda y derecha) con costo unitario, sin movimientos diagonales. La Distancia Manhattan calcula la cantidad mínima exacta de pasos necesarios para llegar de un punto a otro asumiendo la ausencia total de obstáculos. Al no poder existir un camino real más corto que esta distancia, la heurística **nunca sobreestima** el costo verdadero para alcanzar la meta ($h(n) \le h^*(n)$). Al ser admisible, garantiza matemáticamente que el camino encontrado por A\* es óptimo.

---

## Comparación: A* vs. Búsqueda No Informada (Dijkstra)

Al ejecutar ambos algoritmos sobre la misma instancia de cuadrícula y obstáculos se observa una diferencia clara en el comportamiento de la frontera de búsqueda:

* **Dijkstra (no informado):** Al no contar con una heurística ($h(n) = 0$), evalúa los nodos únicamente por su distancia acumulada $g(n)$. Esto provoca que la frontera se expanda de manera uniforme en todas las direcciones (formando un diamante simétrico), desperdiciando cómputo en explorar áreas que se alejan de la meta.
* **A\* (informado):** Gracias a la Distancia Manhattan, la prioridad de los nodos dirige activamente la expansión de la frontera hacia la meta. Esto reduce drásticamente el número de nodos explorados y acelera la convergencia hacia la solución óptima sin sacrificar exactitud.