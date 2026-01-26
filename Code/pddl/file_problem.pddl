(define (problem file) (:domain gui)
(:objects 
    File_Explorer - app
    gonzalo_text_file - file
    Default Downloads - folder
)

(:init
    (empty)
    (current Default)
    (inside Downloads Default)
    (can_create_files Downloads)
    
)

(:goal (and
    (created_file)
))

)
