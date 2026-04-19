import threading
import time
import psutil
import pynvml

pynvml.nvmlInit()
gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)


class Monitor:

    def __init__(self, interval: float = 0.5):
        self.interval = interval
        self.cpu_samples = []
        self.ram_samples = []
        self.gpu_util_samples = []
        self.gpu_mem_samples = []
        self.running = False
        self.thread = None
        self.start_time = None
        self.end_time = None 

    def _take_sample(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        self.cpu_samples.append(cpu)
        self.ram_samples.append(ram)

        util = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)

        gpu_util_pct = util.gpu
        gpu_mem_pct = (mem.used / mem.total) * 100

        self.gpu_util_samples.append(gpu_util_pct)
        self.gpu_mem_samples.append(gpu_mem_pct)

    def _sample_loop(self):
        while self.running:
            self._take_sample()
            time.sleep(self.interval)

    def start(self):
        self.start_time = time.time()
        self.running = True
        self.thread = threading.Thread(target=self._sample_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.end_time = time.time()
        self._print_summary()

    def _print_summary(self):
        print("\n" + "=" * 50)
        print("RESOURCE USAGE SUMMARY")
        print("=" * 50)

        #CPU
        cpu_avg = sum(self.cpu_samples) / len(self.cpu_samples)
        cpu_peak = max(self.cpu_samples)
        print(f"CPU      avg: {cpu_avg:.1f}%   peak: {cpu_peak:.1f}%")

        #RAM
        ram_avg = sum(self.ram_samples) / len(self.ram_samples)
        ram_peak = max(self.ram_samples)
        print(f"RAM      avg: {ram_avg:.1f}%   peak: {ram_peak:.1f}%")

        #GPU utilización
        gpu_util_avg = sum(self.gpu_util_samples) / len(self.gpu_util_samples)
        gpu_util_peak = max(self.gpu_util_samples)
        print(f"GPU util avg: {gpu_util_avg:.1f}%   peak: {gpu_util_peak:.1f}%")

        #GPU memoria
        gpu_mem_avg = sum(self.gpu_mem_samples) / len(self.gpu_mem_samples)
        gpu_mem_peak = max(self.gpu_mem_samples)
        print(f"GPU mem  avg: {gpu_mem_avg:.1f}%   peak: {gpu_mem_peak:.1f}%")

        elapsed = self.end_time - self.start_time
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        print(f"Time     total: {minutes} min {seconds:.2f} s")

        print("=" * 50)