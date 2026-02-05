import os
import subprocess
import time
from pywinauto import Application

def get_everything_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    code_dir = os.path.dirname(script_dir)
    bin_dir = os.path.join(code_dir, "bin", "everything")
    
    return {
        'exe': os.path.join(bin_dir, "everything.exe"),
        'cli': os.path.join(bin_dir, "es.exe"),
        'bin_dir': bin_dir
    }

def init_indexer():
    paths = get_everything_paths()
    exe_path = paths['exe']
    bin_dir = paths['bin_dir']
    db_path = os.path.join(bin_dir, "Everything.db")
    
    first_run = not os.path.exists(db_path)
    
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq everything.exe'],
        capture_output=True,
        text=True
    )
    
    if 'everything.exe' not in result.stdout:
        if first_run:
            print("First run - building index...")
            subprocess.Popen([exe_path], cwd=bin_dir)
            
            time.sleep(2)
            app = Application(backend="win32").connect(title_re=".*Everything.*")
            dlg = app.window(title_re=".*Everything.*")
            dlg.type_keys("{ENTER}")
            time.sleep(2)
            dlg.type_keys("{LEFT}")
            time.sleep(1)
            dlg.type_keys("{ENTER}")
            
            for i in range(60):
                time.sleep(1)
                if os.path.exists(db_path) and os.path.getsize(db_path) > 10000:
                    print(f"Index ready")
                    subprocess.run(['taskkill', '/F', '/IM', 'everything.exe'], capture_output=True)
                    time.sleep(2)
                    subprocess.Popen(
                        [exe_path, '-startup'],
                        cwd=bin_dir,
                        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    time.sleep(3)
                    break
        else:
            subprocess.Popen(
                [exe_path, '-startup'],
                cwd=bin_dir,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("Everything started")
            time.sleep(3)
    else:
        print("Everything running")
    
    return "EverythingIndex"

def search_files(indexer, filename):
    if not indexer:
        return ["Default"]
    
    paths = get_everything_paths()
    cli_path = paths['cli']
    bin_dir = paths['bin_dir']
    
    result = subprocess.run(
        [cli_path, filename],
        capture_output=True,
        text=True,
        timeout=5,
        creationflags=subprocess.CREATE_NO_WINDOW,
        cwd=bin_dir
    )
    
    lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
    
    if not lines:
        print(f"File not found: {filename}")
        return ["Default"]
    
    full_path = lines[0]
    print(f"Found: {full_path}")
    
    folder_path = os.path.dirname(full_path)
    parts = folder_path.split(os.sep)
    
    final_list = ["Default"]
    
    for i, part in enumerate(parts):
        if part.lower() in ['users', 'usuarios']:
            if i + 2 < len(parts):
                final_list.extend(parts[i+2:])
            break
    
    print(f"Path: {final_list}")
    return final_list