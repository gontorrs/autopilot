;Header and description

(define (domain gui)

;remove requirements that are not needed
(:requirements :strips :typing :negative-preconditions)

(:types file app folder text style)

; un-comment following line if constants are needed
;(:constants )

(:predicates
    (open ?v - app)
    (current ?v - folder)
    (inside ?child_folder - folder ?current - folder)
    (file_to ?file - file ?folder - folder)
    (open_file)
    (typed_text)
    (changed_text)
    (text ?text - text)
    (style ?style - style)
)

(:action open
    :parameters (?app - app)
    :precondition (and 
        (not(open ?app)))
    :effect(open ?app)
)

(:action navigate
    :parameters (?app - app ?current - folder ?child - folder)
    :precondition (and 
        (open ?app) (current ?current) (inside ?child ?current)
    )
    :effect (and 
        (current ?child)
        (not(current ?current))
    )
    )

(:action open_file
    :parameters (?app - app ?current - folder ?file - file)
    :precondition (and (open ?app) (current ?current) (file_to ?file ?current) (not (open_file)))
    :effect (and (open_file))
)

(:action type
    :parameters (?app - app ?text - text)
    :precondition (and (open ?app) (not(typed_text)))
    :effect (and (text ?text) (typed_text))
)

(:action search_text
    :parameters (?app - app ?text - text)
    :precondition (and (open ?app))
    :effect (and (text ?text))
)

(:action change_text
    :parameters (?app - app ?text - text ?style - style)
    :precondition (and (open ?app) (not(changed_text)))
    :effect (and (text ?text) (style ?style) (changed_text))
)


    
    
    
    






)