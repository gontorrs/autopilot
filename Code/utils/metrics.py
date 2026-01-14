import GPUtil
import psutil
import threading
import time
from pathlib import Path
import csv

process = psutil.Process()

_monitoring = False
_monitor_thread = None
_cpu_samples = []
_ram_samples = []
_vram_samples = []

def _monitor_resources():
    """Monitorea CPU, RAM y VRAM en segundo plano"""
    global _monitoring, _cpu_samples, _ram_samples, _vram_samples
    
    while _monitoring:
        # CPU
        _cpu_samples.append(process.cpu_percent(interval=0.01))
        
        # RAM
        _ram_samples.append(process.memory_info().rss / 1024 / 1024)
        
        # VRAM
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                _vram_samples.append(gpus[0].memoryUsed)
        except:
            pass
        
        time.sleep(0.1)  # Muestreo cada 100ms

def start_monitoring():
    """Inicia el monitoreo de CPU, RAM y VRAM"""
    global _monitoring, _monitor_thread, _cpu_samples, _ram_samples, _vram_samples
    
    _cpu_samples = []
    _ram_samples = []
    _vram_samples = []
    _monitoring = True
    
    _monitor_thread = threading.Thread(target=_monitor_resources, daemon=True)
    _monitor_thread.start()

def end_monitoring():
    """Finaliza el monitoreo y retorna métricas"""
    global _monitoring, _monitor_thread, _cpu_samples, _ram_samples, _vram_samples
    
    _monitoring = False
    if _monitor_thread:
        _monitor_thread.join(timeout=1)
    
    metrics = {}
    
    if _cpu_samples:
        metrics['cpu_avg'] = sum(_cpu_samples) / len(_cpu_samples)
        metrics['cpu_peak'] = max(_cpu_samples)
    
    if _ram_samples:
        metrics['ram_avg_mb'] = sum(_ram_samples) / len(_ram_samples)
        metrics['ram_peak_mb'] = max(_ram_samples)
    
    if _vram_samples:
        metrics['vram_avg_mb'] = sum(_vram_samples) / len(_vram_samples)
        metrics['vram_peak_mb'] = max(_vram_samples)
    
    return metrics

def append_metric(model_name, **kwargs):
    file_path = Path(__file__).parent.parent / 'data' / 'vlm' / 'metrics_vlm.csv'
    
    file_path.parent.mkdir(exist_ok=True)
    
    rows = []
    headers = ['model']
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = list(reader.fieldnames)
            rows = list(reader)
    
    for key in kwargs.keys():
        if key not in headers:
            headers.append(key)

    new_row = {'model': model_name}
    new_row.update(kwargs)
    rows.append(new_row)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)