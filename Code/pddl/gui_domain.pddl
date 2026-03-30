(define (domain gui)

(:requirements :strips :typing :negative-preconditions)

(:types file app folder text style)

(:predicates
    (empty)
    (open ?v - app)
    (current ?v - folder)
    (inside ?child_folder - folder ?current - folder)
    (file_to ?file - file ?folder - folder)
    ;for destination path
    (text ?text - text)
    (style ?style - style)
    (can_create_files ?folder - folder)
    (in_clipboard ?file - file)
    (is_cut ?file - file)
    (pasted ?file - file ?folder - folder)

    ;goal predicates for each template
    (text_searched ?text - text) ;this one can be used as an end goal or for intermediate goal for change style and delete text.
    (delete_text ?text - text) ;deletes a text
    (open_file ?file - file) ;opens a file in file explorer
    (typed_text ?text - text) ;types text in notepad
    (changed_text ?style - style) ;changed the style of a text in word
    ;these two are predicated for the same template because PDDL cannot use two variables in declarations, but then only use one in actions.
    (new_clicked)
    (naming)
    (created ?text - text)


    
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
    :parameters (?app - app ?text - text ?file - file)
    :precondition (and (open ?app) (not (empty)) (open_file ?file))
    :effect (text_searched ?text)
)

(:action change_text
    :parameters (?app - app ?text - text ?style - style ?file - file)
    :precondition (and (open ?app) (text_searched ?text) (not(changed_text ?style)) (not (empty)) (open_file ?file))
    :effect (and (style ?style) (changed_text ?style))
)

(:action delete_text
    :parameters (?app - app ?text - text ?file - file)
    :precondition (and (open ?app) (text_searched ?text) (not (empty)) (open_file ?file))
    :effect (and (delete_text ?text))
)

(:action copy
    :parameters (?app - app ?file - file ?current - folder)
    :precondition (and (open ?app) (not (empty)) (current ?current) (file_to ?file ?current) (not (in_clipboard ?file)))
    :effect (in_clipboard ?file)
)

(:action cut
    :parameters (?app - app ?file - file ?current - folder)
    :precondition (and (open ?app) (not (empty)) (current ?current) (file_to ?file ?current) (not (in_clipboard ?file)))
    :effect (and (in_clipboard ?file) (is_cut ?file))
)

(:action paste
    :parameters (?app - app ?file - file ?origin - folder ?dest - folder)
    :precondition (and (open ?app) (not (empty)) (in_clipboard ?file) (file_to ?file ?origin) (current ?dest) (not (pasted ?file ?dest)))
    :effect (and(pasted ?file ?dest) (file_to ?file ?dest) (not (in_clipboard ?file)))
)

(:action navigate_back
    :parameters (?app - app ?current - folder ?parent - folder)
    :precondition (and (open ?app) (current ?current) (inside ?current ?parent) (not (empty)))
    :effect (and (current ?parent) (not (current ?current)))
)

(:action click_new
    :parameters (?app - app ?current - folder)
    :precondition (and (open ?app) (current ?current) (can_create_files ?current) (not (empty)))
    :effect (new_clicked)
)

(:action select_type
    :parameters (?app - app)
    :precondition (and (open ?app) (new_clicked) (not (empty)))
    :effect (naming)
)

(:action type_name
    :parameters (?app - app ?text - text)
    :precondition (and (open ?app) (naming) (not (typed_text ?text)) (not (empty)))
    :effect (and (typed_text ?text) (created ?text))
)
    
    
    






)