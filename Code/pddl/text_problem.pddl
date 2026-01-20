(define (problem text) (:domain gui)
(:objects
    Notepad - app
    Hola_me_llamo_Gonzalo - text
)

(:init
    (not (open Notepad))
    (text Hola_me_llamo_Gonzalo)
)

(:goal (and
    (typed_text)
))

)