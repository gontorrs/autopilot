(define (problem change) (:domain gui)
(:objects
    File_Explorer - app
    Hola - text
    italic - style
    Default Desktop - folder
    hello_odt - file
)

(:init
    (empty)
    (current Default)
    (inside Desktop Default)
    (file_to hello_odt Desktop)
)

(:goal (and
    (changed_text italic)
))

)