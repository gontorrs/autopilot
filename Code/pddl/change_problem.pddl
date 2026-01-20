(define (problem change) (:domain gui)
(:objects
    Word - app
    Hola_me_llamo_Gonzalo - text
    bold - style
)

(:init
    (not (open Word))
    (text Hola_me_llamo_Gonzalo)
)

(:goal (and
    (changed_text)
))

)