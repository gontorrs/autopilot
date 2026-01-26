(define (problem navigate) (:domain gui)
(:objects
    Windows_File_Explorer - app
Default Documents TFG Docs - folder
Gonzalo_Anteproyecto_pdf - file
)

(:init
    (empty)
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