from pywinauto import Desktop

def listar_apps_taskbar():
    try:
        # Conectamos al escritorio usando el backend UIA (recomendado para Windows moderno)
        desktop = Desktop(backend="uia")
        
        # Buscamos la barra de tareas principal por su nombre de clase histórico
        taskbar = desktop.window(class_name="Shell_TrayWnd")
        
        # Verificamos si existe antes de seguir
        if not taskbar.exists():
            print("Error: No se encontró la barra de tareas (Shell_TrayWnd).")
            return

        print("--- Aplicaciones detectadas en la Taskbar ---")
        
        # En lugar de buscar contenedores específicos, pedimos TODOS los elementos
        # tipo "Button" que vivan dentro de la barra de tareas.
        # Esto salta las capas invisibles de XAML/WPF de Windows 11.
        all_buttons = taskbar.descendants(control_type="Button")
        
        # Lista de botones del sistema a ignorar para limpiar la salida
        system_buttons = [
            "Inicio", "Start", 
            "Vista de tareas", "Task View", 
            "Búsqueda", "Search", 
            "Widgets", "Chat",
            "Centro de notificaciones", "Notification Center",
            "Mostrar escritorio", "Show desktop",
            "Reloj del sistema", "System Clock"
        ]

        contador = 1
        for btn in all_buttons:
            try:
                # Obtenemos el texto (nombre visible)
                name = btn.window_text()
                
                # A veces el nombre está vacío pero tiene info útil en el legacy_name o help_text
                # pero window_text() suele ser lo que sale en el tooltip.
                
                # Filtramos: que tenga nombre y que no sea un botón del sistema
                if name and name not in system_buttons:
                    print(f"{contador}. {name}")
                    contador += 1
                    
            except Exception:
                # Algunos elementos pueden desaparecer mientras iteramos (tooltips, etc.)
                continue

        if contador == 1:
            print("No se encontraron aplicaciones o los nombres no son legibles.")
            print("Prueba ejecutando la terminal 'Como Administrador' si faltan cosas.")

    except Exception as e:
        print(f"Ocurrió un error general: {e}")

if __name__ == "__main__":
    listar_apps_taskbar()