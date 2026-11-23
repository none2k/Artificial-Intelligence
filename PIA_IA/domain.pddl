(define (domain dron-entregas)
  (:requirements :strips :typing)

  (:types
    dron paquete ubicacion
  )

  (:predicates
    (en ?d - dron ?u - ubicacion)
    (paquete-en ?p - paquete ?u - ubicacion)
    (llevando ?d - dron ?p - paquete)
    (libre ?d - dron)
    (bateria-alta ?d - dron)
    (estacion-carga ?u - ubicacion)
    (destino ?p - paquete ?u - ubicacion)
    (entregado ?p - paquete)
  )

  (:action volar
    :parameters (?d - dron ?desde - ubicacion ?hacia - ubicacion)
    :precondition (and (en ?d ?desde) (bateria-alta ?d))
    :effect (and (en ?d ?hacia)
                 (not (en ?d ?desde))
                 (not (bateria-alta ?d)))
  )

  (:action recargar
    :parameters (?d - dron ?u - ubicacion)
    :precondition (and (en ?d ?u) (estacion-carga ?u))
    :effect (bateria-alta ?d)
  )

  (:action recoger
    :parameters (?d - dron ?p - paquete ?u - ubicacion)
    :precondition (and (en ?d ?u) (paquete-en ?p ?u) (libre ?d))
    :effect (and (llevando ?d ?p)
                 (not (paquete-en ?p ?u))
                 (not (libre ?d)))
  )

  (:action entregar
    :parameters (?d - dron ?p - paquete ?u - ubicacion)
    :precondition (and (en ?d ?u) (llevando ?d ?p) (destino ?p ?u))
    :effect (and (entregado ?p)
                 (libre ?d)
                 (not (llevando ?d ?p)))
  )
)