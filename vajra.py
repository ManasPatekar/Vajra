import os
import sys
import time
import gc
import psutil
import platform
import logging
from datetime import datetime
from typing import Dict, Any
from collections import deque
from logging.handlers import RotatingFileHandler

from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.console import Console


# =========================
# LOGGING
# =========================

def setup_logging():
    log_handler = RotatingFileHandler(
        "vajra.log",
        maxBytes=1024 * 1024,  # 1 MB
        backupCount=3
    )
    log_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    log_handler.setFormatter(log_formatter)

    logger = logging.getLogger("Vajra")
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    return logger

logger = setup_logging()


# =========================
# CACHE CLEANER
# =========================

class CacheCleaner:
    """
    Permission-silent RAM cache cleaner.
    Never requests admin privileges.
    Best-effort only (OS-safe).
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.os_type = platform.system().lower()

    def clean(self) -> bool:
        self.logger.info("RAM cleanup triggered (best-effort)")
        success = False

        try:
            gc.collect()
            success = True

            if self.os_type == "windows":
                success |= self._windows_trim()
            elif self.os_type == "linux":
                success |= self._linux_trim()
            elif self.os_type == "darwin":
                success |= self._mac_trim()

        except Exception as e:
            self.logger.error(f"RAM cleanup error: {e}")

        return success

    def _windows_trim(self) -> bool:
        # iterate through all processes to trim working sets
        import ctypes
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400
        
        count = 0
        for pid in psutil.pids():
            try:
                # Open process with necessary permissions
                handle = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                if handle:
                    psapi.EmptyWorkingSet(handle)
                    kernel32.CloseHandle(handle)
                    count += 1
            except Exception:
                pass
        
        if count > 0:
            self.logger.info(f"Trimmed working set for {count} processes")
            return True
        return False

    def _linux_trim(self) -> bool:
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            if hasattr(libc, "malloc_trim"):
                libc.malloc_trim(0)
                self.logger.info("Linux malloc_trim executed")
                return True
        except Exception:
            pass
        return False

    def _mac_trim(self) -> bool:
        try:
            return os.system("purge >/dev/null 2>&1") == 0
        except Exception:
            return False


# =========================
# ALERT MANAGER
# =========================

class AlertManager:
    def __init__(self, cleaner: CacheCleaner):
        self.cleaner = cleaner
        self.last_trigger = {}
        self.cooldown = 60  # seconds

        self.thresholds = {
            "cpu": 85,
            "memory": 90  # Increased to match image (92%) closer
        }

    def check(self, metrics: Dict[str, Any], ui_callback=None):
        alerts = []
        now = time.time()

        # CPU
        if metrics["cpu"]["percent"] > self.thresholds["cpu"]:
            alerts.append(f"High CPU usage: {metrics['cpu']['percent']}%")

        # MEMORY
        if metrics["memory"]["percent"] > self.thresholds["memory"]:
            last = self.last_trigger.get("memory", 0)
            if now - last > self.cooldown:
                self.last_trigger["memory"] = now

                if ui_callback:
                    ui_callback(f"High memory ({metrics['memory']['percent']}%) detected. Cleaning RAM...")

                cleaned = self.cleaner.clean()

                if ui_callback:
                    if cleaned:
                        ui_callback("RAM cleanup completed (best-effort)")
                    else:
                        ui_callback("RAM cleanup skipped (OS restricted)")

                alerts.append(f"High Memory usage: {metrics['memory']['percent']}%")

        return alerts


# =========================
# DASHBOARD
# =========================

        return alerts


# =========================
# DASHBOARD
# =========================

# =========================
# DASHBOARD
# =========================

class SysMonDashboard:
    def __init__(self):
        self.logs = []
        # Cache static info
        self._sys_info = f"{platform.system()} {platform.release()}"
        self._node_name = platform.node()
        self._app_title = Text("Vajra v1.0", style="bold white")
        
        # CPU Info
        self.phys_cores = psutil.cpu_count(logical=False) or 1
        self.log_cores = psutil.cpu_count(logical=True) or 1

    def update_history(self, metrics):
        # Placeholder compatible method if needed, or we can just remove it from main loop
        pass

    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        self.logs = self.logs[-10:]

    def header(self):
        table = Table(show_header=False, expand=True, box=None)
        table.add_column(justify="left")
        table.add_column(justify="right")

        table.add_row(
            self._app_title,
            Text(f"{self._node_name} • {self.phys_cores}P/{self.log_cores}L Cores • {datetime.now().strftime('%H:%M:%S')}", style="dim white")
        )

        return Panel(table, style="white on blue", box=box.SQUARE)

    def _get_color(self, value):
        return "green" if value < 50 else "yellow" if value < 80 else "bold red"

    def _make_bar(self, value, width=20):
        color = self._get_color(value)
        filled = int((value / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{color}]{bar}[/] {value:>3.0f}%"

    def _format_gb(self, bytes_val):
        try:
            return f"{bytes_val / (1024**3):.1f} GB"
        except (TypeError, ValueError):
            return "0.0 GB"

    def stats_panel(self, metrics):
        table = Table(box=box.SIMPLE, expand=True)
        table.add_column("Resource", style="bold white")
        table.add_column("Usage")
        table.add_column("Details", justify="right", style="dim white")
        
        # CPU Total
        freq = metrics.get('cpu_freq', 0)
        freq_str = f"{freq/1000:.2f} GHz" if freq else ""
        table.add_row(
            "CPU", 
            self._make_bar(metrics['cpu']['percent']),
            freq_str
        )
        
        # Memory
        mem = metrics.get('memory', {})
        used = mem.get('used', 0)
        total = mem.get('total', 1)
        avail = mem.get('available', 0)
        percent = mem.get('percent', 0)
        
        mem_str = f"{self._format_gb(used)}/{self._format_gb(total)} ({self._format_gb(avail)} Free)"
        table.add_row(
            "RAM", 
            self._make_bar(percent),
            mem_str
        )
        
        # Disks
        disks = metrics.get('disks', {})
        for d_name, d_usage in disks.items():
            free_bytes = d_usage.get('free', 0)
            percent = d_usage.get('percent', 0)
            free_gb = f"{self._format_gb(free_bytes)} Free"
            table.add_row(
                f"Disk {d_name}", 
                self._make_bar(percent),
                free_gb
            )

        # Network
        sent = metrics.get('net_sent', 0)
        recv = metrics.get('net_recv', 0)
        net_text = f"↑ {self._format_bytes(sent)}  ↓ {self._format_bytes(recv)}"
        table.add_row("Network", "", net_text)

        return Panel(table, title="[bold]Overview[/]", border_style="cyan")

    def cores_panel(self, metrics):
        # Create a grid for cores (2 columns)
        table = Table(box=None, show_header=False, expand=True)
        table.add_column(ratio=1)
        table.add_column(ratio=1)

        cores = metrics['per_core']
        for i in range(0, len(cores), 2):
            c1 = cores[i]
            c1_str = f"C{i+1:02d}: {self._make_bar(c1, width=10)}"
            
            c2_str = ""
            if i + 1 < len(cores):
                c2 = cores[i+1]
                c2_str = f"C{i+2:02d}: {self._make_bar(c2, width=10)}"
            
            table.add_row(c1_str, c2_str)

        return Panel(table, title="[bold]Core Usage[/]", border_style="magenta")

    def processes_panel(self, metrics):
        table = Table(box=box.SIMPLE, show_header=True, expand=True)
        table.add_column("PID", width=6)
        table.add_column("Name", no_wrap=True)
        table.add_column("CPU%", justify="right")
        table.add_column("Mem%", justify="right")

        for p in metrics['top_procs']:
            table.add_row(
                str(p['pid']),
                p['name'],
                f"{p['cpu_percent']:.1f}",
                f"{p['memory_percent']:.1f}"
            )
        
        return Panel(table, title="[bold]Top Processes[/]", border_style="green")

    def log_panel(self):
        if not self.logs:
            return Panel(Text("No active events...", style="dim italic"), title="[bold]Event Log[/]", border_style="blue")
            
        table = Table(box=None, show_header=False, expand=True)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Message")

        for log_entry in self.logs:
            try:
                ts_part, msg_part = log_entry.split(']', 1)
                ts = ts_part.strip('[')
                msg = msg_part.strip()
                
                if "High" in msg: style = "bold red"
                elif "cleanup" in msg: style = "green"
                else: style = "white"
                    
                table.add_row(ts, Text(msg, style=style))
            except:
                table.add_row("-", log_entry)

        return Panel(table, title="[bold]Event Log[/]", border_style="blue")

    def layout(self, metrics):
        layout = Layout()
        layout.split_column(
            Layout(self.header(), size=3),
            Layout(name="main")
        )

        layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )

        layout["left"].split_column(
            Layout(self.stats_panel(metrics), size=12),
            Layout(self.cores_panel(metrics))
        )

        layout["right"].split_column(
            Layout(self.processes_panel(metrics), ratio=1),
            Layout(self.log_panel(), ratio=1)
        )
        
        return layout

    def _format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.1f} {power_labels[n]}B/s"


# =========================
# METRICS
# =========================

class MetricsCollector:
    def __init__(self):
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()
        self.procs = {}  # {pid: ProcessObj} cache
        self.cached_top_procs = []
        self.tick = 0
        
        # Seed CPU
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None, percpu=True)

    def collect(self):
        now = time.time()
        net = psutil.net_io_counters()
        
        # Network Rates
        dt = now - self.last_time
        if dt == 0: dt = 0.001
        
        sent_per_sec = (net.bytes_sent - self.last_net.bytes_sent) / dt
        recv_per_sec = (net.bytes_recv - self.last_net.bytes_recv) / dt

        self.last_net = net
        self.last_time = now

        # Process Monitoring (Throttled to save CPU)
        # Only scan processes every 4th cycle (approx every 2 seconds)
        self.tick += 1
        top_procs = self.cached_top_procs
        
        if self.tick % 4 == 0:
            try:
                current_pids = set(psutil.pids())
                cached_pids = set(self.procs.keys())
                
                # Remove dead
                for pid in cached_pids - current_pids:
                    del self.procs[pid]
                
                proc_list = []
                # Use process_iter with filters to minimize object creation overhead
                # We need to iterate all to find the top ones
                for p in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                    try:
                        pid = p.info['pid']
                        if pid not in self.procs:
                            # New process, use the object from iter
                            self.procs[pid] = p
                            # First call to cpu_percent returns 0.0 usually, which is fine
                            p.cpu_percent(interval=None) 
                        else:
                            # Use cached object to get accurate cpu diff
                            p = self.procs[pid]
                        
                        # Store info for sorting
                        # We need to re-fetch info to be safe
                        with p.oneshot():
                             p_cpu = p.cpu_percent(interval=None)
                             p_mem = p.memory_percent()
                             p_name = p.name()
                             
                        proc_list.append({
                            'pid': pid,
                            'name': p_name,
                            'cpu_percent': p_cpu,
                            'memory_percent': p_mem
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        if pid in self.procs:
                            del self.procs[pid]
                        continue
                
                # Sort by CPU and top 5
                top_procs = sorted(proc_list, key=lambda x: x['cpu_percent'], reverse=True)[:5]
                self.cached_top_procs = top_procs
                
            except Exception:
                pass

        # Disks
        disks = {}
        for part in psutil.disk_partitions(all=False):
            if 'cdrom' in part.opts or part.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                # Use mountpoint or device as name (e.g. "C:\" or "/dev/sda1")
                name = part.device
                disks[name] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                }
            except PermissionError:
                continue

        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=None),
            },
            "cpu_freq": getattr(psutil.cpu_freq(), 'current', 0.0),
            "per_core": psutil.cpu_percent(interval=None, percpu=True),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "total": psutil.virtual_memory().total,
                "used": psutil.virtual_memory().used,
                "available": psutil.virtual_memory().available
            },
            "disks": disks,
            "net_sent": sent_per_sec,
            "net_recv": recv_per_sec,
            "top_procs": top_procs
        }


# =========================
# MAIN LOOP
# =========================

def print_help():
    print("""
Vajra - System Monitor & Cleaner
Usage: vajra.py [COMMAND]

Commands:
  start     Start the live dashboard (Default)
  logs      Follow the tail of vajra.log
  help      Show this help message
""")

def show_splash():
    """Display startup splash screen"""
    console = Console()
    ascii_art = r"""
 [bold cyan]
 __      __        _             
 \ \    / /       (_)            
  \ \  / /_ _  ___ _ _ __ __ _   
   \ \/ / _` |/ __| | '__/ _` |  
    \  / (_| | (__| | | | (_| |  
     \/ \__,_|\___| |_|  \__,_|  
 [/bold cyan][bold white]      SYSTEM SENTINEL v1.0[/]
    """
    console.print(ascii_art, justify="center")
    console.print("\n[dim]Initializing guardian protocols...[/dim]", justify="center")
    time.sleep(1.5)

def tail_logs():
    print("Following vajra.log (Ctrl+C to stop)...")
    try:
        with open("vajra.log", "r") as f:
            # Go to the end
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                print(line, end="")
    except FileNotFoundError:
        print("Error: vajra.log not found.")
    except KeyboardInterrupt:
        print("\nStopped.")

def start_monitor():
    cleaner = CacheCleaner(logger)
    alert_manager = AlertManager(cleaner)
    dashboard = SysMonDashboard()
    collector = MetricsCollector()

    print("Initializing components... (Ctrl+C to exit)")
    
    try:
        with Live(refresh_per_second=2, screen=True) as live:
            while True:
                metrics = collector.collect()
                dashboard.update_history(metrics)
                alerts = alert_manager.check(metrics, ui_callback=dashboard.add_log)

                for alert in alerts:
                    dashboard.add_log(alert)
                    logger.warning(alert)

                live.update(dashboard.layout(metrics))
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass

def main():
    cmd = "start"
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

    if cmd == "start":
        show_splash()
        start_monitor()
    elif cmd == "logs":
        tail_logs()
    elif cmd == "help":
        print_help()
    else:
        print(f"Unknown command: {cmd}")
        print_help()

if __name__ == "__main__":
    main()
