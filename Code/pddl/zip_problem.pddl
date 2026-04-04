(define (problem compress_files)

(:domain gui)

(:objects
    file_explorer - app
    default - folder
    documents - folder
    report - file
    data - file
)

(:init
    (empty)
    (current default)
    (inside documents default)
    (file_to report documents)
    (file_to data documents)
)

(:goal (and
    (selected report)
    (selected data)
    (zipped)
))
)