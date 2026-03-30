(define (problem copy_paste) (:domain gui)
(:objects
    File_Explorer - app
    Default Downloads TFG Documents - folder
    gonzalo_doc - file
)

(:init
    (empty)
    (current Default)
    (inside Downloads Default)
    (inside TFG Downloads)
    (inside Documents Default)
    (file_to gonzalo_doc TFG)
)

(:goal (and
    ;(is_cut gonzalo_doc) ;en caso de querer cortar en lugar de copy paste.
    (pasted gonzalo_doc Documents)
))
)