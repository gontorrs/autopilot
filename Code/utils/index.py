import os
import win32com.client

def init_indexer():
    # No initialization needed for Windows Search
    print("Connected to Windows Search Index (Native)")
    return "WindowsIndex"


def search_files(indexer, filename):
    filename = filename.strip()
    raw_paths = []
    
    # 1. SQL Query to Windows SystemIndex
    sql = f"""
        SELECT System.ItemPathDisplay 
        FROM SystemIndex 
        WHERE System.ItemName LIKE '%{filename}%'
        AND System.Kind <> 'folder'
    """
    
    try:
        connector = win32com.client.Dispatch("ADODB.Connection")
        connector.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
        
        # Execute Query
        recordset = connector.Execute(sql)[0]
        
        while not recordset.EOF:
            path = str(recordset.Fields.Item(0).Value)
            raw_paths.append(path)
            recordset.MoveNext()
            # We only need the best match
            if len(raw_paths) >= 1: 
                break
                
        connector.Close()

    except Exception as e:
        print(f"Windows Search Error: {e}")
    
    if not raw_paths:
        raw_paths = None
        
    if not raw_paths:
        return []

    full_path = raw_paths[0]
    
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

    return final_list