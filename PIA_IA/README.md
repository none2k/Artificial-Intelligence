# PIA — Planificación Automatizada con PDDL: Dron de Entregas

**Alumno:** Miguel Puente Flores  
**Dominio:** `dron-entregas`  
**Herramienta:** [editor.planning.domains](https://editor.planning.domains/)  
**Video Demo:** https://drive.google.com/file/d/1ICQvs0CqDGQCV7ymlCLj1bEqYc_doRch/view?usp=sharing

---

## 1. Descripción del Escenario
Este proyecto modela la logística de un dron autónomo encargado de recoger y entregar paquetes en un entorno urbano. A diferencia de un transporte convencional, el dron tiene autonomía limitada: cada vuelo consume su batería, por lo que debe planificar paradas estratégicas en estaciones de carga para completar la entrega y regresar a su base.

---

## 2. Proceso de Diseño

### A. Elección de Predicados (8 en total)
Para representar el estado del mundo con precisión, se definieron los siguientes predicados:

| Predicado | Propósito en el diseño |
| :--- | :--- |
| `(en ?d ?u)` | Rastrea la ubicación actual del dron. |
| `(paquete-en ?p ?u)` | Indica dónde se encuentra un paquete antes de ser recogido. |
| `(llevando ?d ?p)` | Modela que el dron está transportando un paquete específico. |
| `(libre ?d)` | Restringe la capacidad del dron a un solo paquete a la vez. |
| `(bateria-alta ?d)` | Controla si el dron tiene energía suficiente para despegar. |
| `(estacion-carga ?u)` | Define qué ubicaciones cuentan con infraestructura para recargar. |
| `(destino ?p ?u)` | Evita que el paquete se entregue en una ubicación incorrecta. |
| `(entregado ?p)` | Permite verificar el cumplimiento de la meta de entrega. |

### B. Diseño de Acciones (4 esquemas)
Durante el diseño se identificó que el ciclo de vida de una entrega requiere cuatro operaciones fundamentales:

1. **`volar`**: Se diseñó con la precondición `(bateria-alta ?d)` y el efecto negativo `(not (bateria-alta ?d))`. Esto asegura que el dron no pueda encadenar dos vuelos seguidos sin recargar.
2. **`recargar`**: Requiere que el dron esté en una ubicación marcada como `(estacion-carga ?u)` y restaura `(bateria-alta ?d)`.
3. **`recoger`**: Exige que el dron y el paquete coincidan en la misma ubicación y que el dron esté `(libre ?d)`, evitando que cargue múltiples paquetes simultáneamente.
4. **`entregar`**: Valida que la ubicación actual coincida con `(destino ?p ?u)` antes de marcar el paquete como `(entregado ?p)` y liberar al dron.

---

## 3. Diferencias con Dominios de Inspiración
Este dominio toma como punto de partida la idea general de transporte de **Air Cargo**, pero introduce cambios estructurales propios que alteran la lógica de planificación:

* **Gestión de energía (consumo y recarga):** En *Air Cargo*, los aviones pueden volar indefinidamente entre aeropuertos. Aquí, volar consume la batería y obliga al planificador a intercalar acciones de `recargar` en ubicaciones válidas.
* **Capacidad unitaria explícita:** Se agregó el predicado `(libre ?d)` para modelar la limitación física de un dron pequeño (solo un paquete a la vez).
* **Validación de destino y estado final:** En lugar de solo verificar la ubicación del paquete en la meta, se incorporaron `(destino ?p ?u)` y `(entregado ?p)` para asegurar una entrega formal.
* **Retorno obligatorio:** El problema exige tanto la entrega como el regreso del dron a la base, lo que fuerza un plan de **7 pasos** en lugar de una ruta lineal simple.

---

## 4. Plan Encontrado (7 pasos)
Al ejecutar `domain.pddl` y `problem.pddl` en `editor.planning.domains`, el planificador genera la siguiente secuencia:

1. `(volar dron1 base almacen)`
2. `(recoger dron1 paq1 almacen)`
3. `(recargar dron1 almacen)`
4. `(volar dron1 almacen cliente)`
5. `(entregar dron1 paq1 cliente)`
6. `(recargar dron1 cliente)`
7. `(volar dron1 cliente base)`

---

## 5. Visualización en Python
Se incluye el script `dron_visual.py` desarrollado en Python con `pygame` para visualizar paso a paso el estado del mundo, las precondiciones, los efectos y el cumplimiento de metas.

**Ejecución:**
```bash
pip install pygame
python dron_visual.py