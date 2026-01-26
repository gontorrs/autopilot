(define (problem change) (:domain gui)
(:objects
    File_Explorer - app
    Hola_me_llamo_Gonzalo - text
    bold - style
    Default Downloads - folder
    gonzalo_doc - file
)

(:init
    (empty)
    (current Default)
    (inside Downloads Default)
    (file_to gonzalo_doc Downloads)
)

(:goal (and
    (changed_text)
))

)