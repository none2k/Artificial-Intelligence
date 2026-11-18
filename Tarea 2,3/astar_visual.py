import pygame
from queue import PriorityQueue

# Configuración de la ventana
ANCHO = 600
VENTANA = pygame.display.set_mode((ANCHO, ANCHO))
pygame.display.set_caption("Búsqueda A* - Visualización")

# Colores para los estados de los nodos
BLANCO = (255, 255, 255)  # No visitado
NEGRO = (0, 0, 0)         # Obstáculo
ROJO = (255, 0, 0)        # Frontera explorada (Cerrado)
VERDE = (0, 255, 0)       # Frontera por explorar (Abierto)
AZUL = (0, 0, 255)        # Camino final
AMARILLO = (255, 255, 0)  # Inicio
MORADO = (128, 0, 128)    # Meta
GRIS = (128, 128, 128)    # Líneas de cuadrícula

class Nodo:
    def __init__(self, fila, col, ancho_celda, total_filas):
        self.fila = fila
        self.col = col
        self.x = fila * ancho_celda
        self.y = col * ancho_celda
        self.color = BLANCO
        self.vecinos = []
        self.ancho = ancho_celda
        self.total_filas = total_filas

    def get_pos(self): return self.fila, self.col
    def es_obstaculo(self): return self.color == NEGRO
    def hacer_inicio(self): self.color = AMARILLO
    def hacer_obstaculo(self): self.color = NEGRO
    def hacer_meta(self): self.color = MORADO
    def hacer_cerrado(self): self.color = ROJO
    def hacer_abierto(self): self.color = VERDE
    def hacer_camino(self): self.color = AZUL
    def dibujar(self, ventana): pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))

    def actualizar_vecinos(self, cuadricula):
        self.vecinos = []
        # Abajo, Arriba, Derecha, Izquierda (sin diagonales)
        if self.fila < self.total_filas - 1 and not cuadricula[self.fila + 1][self.col].es_obstaculo():
            self.vecinos.append(cuadricula[self.fila + 1][self.col])
        if self.fila > 0 and not cuadricula[self.fila - 1][self.col].es_obstaculo():
            self.vecinos.append(cuadricula[self.fila - 1][self.col])
        if self.col < self.total_filas - 1 and not cuadricula[self.fila][self.col + 1].es_obstaculo():
            self.vecinos.append(cuadricula[self.fila][self.col + 1])
        if self.col > 0 and not cuadricula[self.fila][self.col - 1].es_obstaculo():
            self.vecinos.append(cuadricula[self.fila][self.col - 1])

def heuristica(p1, p2):
    # Distancia Manhattan
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruir_camino(nodos_previos, actual, dibujar):
    while actual in nodos_previos:
        actual = nodos_previos[actual]
        actual.hacer_camino()
        dibujar()

def algoritmo_astar(dibujar, cuadricula, inicio, meta):
    contador = 0
    frontera = PriorityQueue()
    frontera.put((0, contador, inicio))
    nodos_previos = {}
    
    g_score = {nodo: float("inf") for fila in cuadricula for nodo in fila}
    g_score[inicio] = 0
    f_score = {nodo: float("inf") for fila in cuadricula for nodo in fila}
    f_score[inicio] = heuristica(inicio.get_pos(), meta.get_pos())
    
    frontera_hash = {inicio}

    while not frontera.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        actual = frontera.get()[2]
        frontera_hash.remove(actual)

        if actual == meta:
            reconstruir_camino(nodos_previos, meta, dibujar)
            meta.hacer_meta()
            inicio.hacer_inicio()
            return True

        for vecino in actual.vecinos:
            temp_g_score = g_score[actual] + 1

            if temp_g_score < g_score[vecino]:
                nodos_previos[vecino] = actual
                g_score[vecino] = temp_g_score
                f_score[vecino] = temp_g_score + heuristica(vecino.get_pos(), meta.get_pos())
                if vecino not in frontera_hash:
                    contador += 1
                    frontera.put((f_score[vecino], contador, vecino))
                    frontera_hash.add(vecino)
                    vecino.hacer_abierto()
        
        dibujar()
        if actual != inicio:
            actual.hacer_cerrado()
            
    return False

# Funciones auxiliares de dibujado (simplificadas)
def hacer_cuadricula(filas, ancho):
    ancho_celda = ancho // filas
    return [[Nodo(i, j, ancho_celda, filas) for j in range(filas)] for i in range(filas)]

def dibujar_lineas(ventana, filas, ancho):
    ancho_celda = ancho // filas
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_celda), (ancho, i * ancho_celda))
        for j in range(filas):
            pygame.draw.line(ventana, GRIS, (j * ancho_celda, 0), (j * ancho_celda, ancho))

def dibujar(ventana, cuadricula, filas, ancho):
    ventana.fill(BLANCO)
    for fila in cuadricula:
        for nodo in fila:
            nodo.dibujar(ventana)
    dibujar_lineas(ventana, filas, ancho)
    pygame.display.update()

def main(ventana, ancho):
    FILAS = 30
    cuadricula = hacer_cuadricula(FILAS, ancho)
    inicio = None
    meta = None
    corriendo = True

    while corriendo:
        dibujar(ventana, cuadricula, FILAS, ancho)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: corriendo = False
            
            # Click izquierdo: colocar inicio, meta u obstáculo
            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                fila, col = pos[0] // (ancho // FILAS), pos[1] // (ancho // FILAS)
                nodo = cuadricula[fila][col]
                if not inicio and nodo != meta:
                    inicio = nodo
                    inicio.hacer_inicio()
                elif not meta and nodo != inicio:
                    meta = nodo
                    meta.hacer_meta()
                elif nodo != inicio and nodo != meta:
                    nodo.hacer_obstaculo()

            # Click derecho: borrar
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                fila, col = pos[0] // (ancho // FILAS), pos[1] // (ancho // FILAS)
                nodo = cuadricula[fila][col]
                nodo.color = BLANCO
                if nodo == inicio: inicio = None
                if nodo == meta: meta = None

            # Presionar Espacio: iniciar algoritmo
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and inicio and meta:
                    for fila in cuadricula:
                        for nodo in fila:
                            nodo.actualizar_vecinos(cuadricula)
                    algoritmo_astar(lambda: dibujar(ventana, cuadricula, FILAS, ancho), cuadricula, inicio, meta)
                
                # Presionar 'C': limpiar tablero
                if event.key == pygame.K_c:
                    inicio, meta = None, None
                    cuadricula = hacer_cuadricula(FILAS, ancho)

    pygame.quit()

if __name__ == "__main__":
    main(VENTANA, ANCHO)