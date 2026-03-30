(define (problem create_test)
  (:domain gui)
  (:objects
    file_explorer - app
    default documents - folder
    gts - folder
    gts_name - text
  )
  (:init
    (empty)
    (current default)
    (inside documents default)
    (can_create_files documents)
  )
  (:goal (created gts_name))
)