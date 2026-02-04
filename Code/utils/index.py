import os
import time
import subprocess
from everytools import EveryTools

# Creating the intit file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
EXE_PATH = os.path.join(BIN_DIR, "Everything.exe")
INI_PATH = os.path.join(BIN_DIR, "Everything.ini")


def _configure():
    if not os.path.exists(INI_PATH):
        try:
            with open(INI_PATH, "w") as f:
                f.write("[Everything]\n")
                f.write("run_in_background=1\n")
                f.write("show_tray_icon=0\n")
                f.write("check_for_updates_on_startup=0\n")
                f.write("allow_http_server=0\n")
                f.write("allow_etp_server=0\n")
        except:
            pass


def init_indexer():
    try:
        return EveryTools()
    except:
        pass

    # 2. Verify the executable exists
    if not os.path.exists(EXE_PATH):
        print(f"Error: Could not find '{EXE_PATH}'")
        return None

    # 3. Configure and start in service mode
    _configure()
    
    try:
        # try and launch with no gui
        subprocess.Popen([EXE_PATH, "-startup"])
        time.sleep(1) # Short wait for memory load
        return EveryTools()
    except Exception as e:
        print(f"Error starting engine: {e}")
        return None


def search_files(indexer, filename):
    if not indexer: return []
    try:
        raw_paths = list(indexer.search_name(filename))
        normalized_results = []

        for full_path in raw_paths:
            folder_path = os.path.dirname(full_path)
            parts = folder_path.split(os.sep)
            clean_parts = [p for p in parts if p]
            
            cut_index = 0
            for i, part in enumerate(clean_parts):
                if part.lower() in ['users', 'usuarios']:
                    if i + 2 < len(clean_parts):
                        cut_index = i + 2
                        break
            
            final_list = ["Default"]
            
            if cut_index > 0:
                final_list.extend(clean_parts[cut_index:])
            else:
                if ':' in clean_parts[0]:
                    final_list.extend(clean_parts[1:])
                else:
                    final_list.extend(clean_parts)
            
            normalized_results.append(final_list)

        return normalized_results
    except:
        return []