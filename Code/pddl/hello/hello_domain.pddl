(define (domain hello)
    (:requirements :strips :negative-preconditions :typing)

    (:types bloque ubicacion)
    
    (:predicates
    (onarm ?v - bloque)
    (clear ?v - bloque)
    (position ?v - bloque ?pos - ubicacion)
    (armEmpty))

    (:action pick
    :parameters (?v - bloque ?top - ubicacion)
    :precondition (and (not (onarm ?v)) (clear ?v) (armEmpty) (position ?v ?top))
    :effect (and (onarm ?v) (not(clear ?v)) (not (armEmpty)) (not (position ?v ?top))))

    (:action drop
    :parameters (?v - bloque ?table - ubicacion)
    :precondition (and 
        (onarm ?v) (not (clear ?v)) (not (armEmpty))
    )
    :effect (and 
        (not (onarm ?v)) (clear ?v) (armEmpty) (position ?v ?table))))