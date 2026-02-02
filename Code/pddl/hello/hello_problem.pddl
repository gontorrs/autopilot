(define (problem test) (:domain hello)
(:objects
    A B - bloque
    top table - ubicacion
)

(:init
    (position A table)
    (position B top)
    (clear A)
    (clear B)
    (armEmpty)
)

(:goal (and
    (position A top)
    (position B table)
))
)
