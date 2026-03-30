(define (domain gui)

(:requirements :strips :typing :negative-preconditions)

(:types file app folder text style)

(:predicates
    (empty)
    (open ?v - app)
    (current ?v - folder)
    (inside ?child_folder - folder ?current - folder)
    (file_to ?file - file ?folder - folder)

    (open_file ?file - file)
    (typed_text ?text - text)
    (changed_text ?style - style)
    (created_file ?file - file)

    (text ?text - text)
    (text_searched ?text - text)
    (style ?style - style)
    (can_create_files ?folder - folder)
)

(:action open
    :parameters (?app - app)
    :precondition (and 
        (not(open ?app)) (empty))
    :effect(and (open ?app) (not(empty)))
)

(:action navigate
    :parameters (?app - app ?current - folder ?child - folder)
    :precondition (and 
        (open ?app) (current ?current) (inside ?child ?current) (not (empty))
    )
    :effect (and 
        (current ?child)
        (not(current ?current))
    )
    )

(:action open_file
    :parameters (?app - app ?current - folder ?file - file)
    :precondition (and (open ?app) (current ?current) (file_to ?file ?current) (not (open_file ?file)) (not (empty)))
    :effect (and (open_file ?file))
)

(:action type
    :parameters (?app - app ?text - text)
    :precondition (and (open ?app) (not(typed_text ?text)) (not (empty)))
    :effect (and (text ?text) (typed_text ?text))
)

(:action search_text
    :parameters (?app - app ?text - text ?file - file ?style - style)
    :precondition (and (open ?app) (not(changed_text ?style)) (not (empty)) (open_file ?file))
    :effect (text_searched ?text)
)

(:action change_text
    :parameters (?app - app ?text - text ?style - style ?file - file)
    :precondition (and (open ?app) (text_searched ?text) (not(changed_text ?style)) (not (empty)) (open_file ?file))
    :effect (and (style ?style) (changed_text ?style))
)

(:action create_file
    :parameters (?app - app ?file - file ?current - folder)
    :precondition (and (open ?app) (current ?current) (not(created_file ?file)) (not (empty)) (can_create_files ?current))
    :effect (and (created_file ?file) (file_to ?file ?current))
)



    
    
    
    






)