(define (problem files) (:domain gui)
(:objects
    File_Explorer - app
    Default Documents TFG Docs - folder
    Gonzalo_Anteproyecto_pdf - file
)

(:init
    (current Default)
    (inside Documents Default)
    (inside TFG Documents)
    (inside Docs TFG)
    (file_to Gonzalo_Anteproyecto_pdf Docs)
)

(:goal (and
    (open_file)
))

)
