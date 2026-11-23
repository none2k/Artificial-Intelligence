(define (problem entrega-urbana-1)
  (:domain dron-entregas)

  (:objects
    dron1 - dron
    paq1 - paquete
    base almacen cliente - ubicacion
  )

  (:init
    (en dron1 base)
    (bateria-alta dron1)
    (libre dron1)
    (paquete-en paq1 almacen)
    (destino paq1 cliente)
    (estacion-carga base)
    (estacion-carga almacen)
    (estacion-carga cliente)
  )

  (:goal
    (and (entregado paq1)
         (en dron1 base))
  )
)