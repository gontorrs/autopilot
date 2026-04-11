(define (problem navigate_problem)
  (:domain gui)
  (:objects
 file_explorer - app
default documents tfg docs - folder
gonzalo_anteproyecto_pdf - file
)
  (:init
    (empty)
(current default)
(inside documents default)
(inside tfg documents)
(inside docs tfg)
(file_to gonzalo_anteproyecto_pdf docs)
  )
  (:goal (open_file gonzalo_anteproyecto_pdf))
)
