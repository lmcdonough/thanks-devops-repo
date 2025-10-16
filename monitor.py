import psutil
import json
import argparse
import sys
from datetime import datetime, timezone

# Parse command-line arguments for dynamic threshold configuration
def parse_args():
    parser = argparse.ArgumentParser(description='System health monitor')
    parser.add_argument('--cpu-threshold', type=float, default=80.0, help='CPU usage threshold percentage (default: 80:0)')
    parser.add_argument('--memory-threshold', type=float, default=85.0, help='Memory usage threshold percentage (default: 85:0)')
    parser.add_argument('--disk-threshold', type=float, default=90.0, help='Disk usage threshold percentage (default: 90)')
    return parser.parse_args()

# Collect system metrics using psutil library
def collect_metrics():
    # interval=1 forces actual CPU usage measurement vs instant snapshot
    cpu_percent = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'disk_percent': disk_percent
    }

# Compare metrics agains thresholds and determine status
def check_health(metrics, thresholds):
    alerts = []
    
    # Check each metric against its configured threshold
    if metrics['cpu_percent'] > thresholds.cpu_threshold:
        alerts.append(f"CPU usage high: {metrics['cpu_percent']}%")
    if metrics['memory_percent'] > thresholds.memory_threshold:
        alerts.append(f"Memory usage high: {metrics['memory_percent']}%")
    if metrics['disk_percent'] > thresholds.disk_threshold:
        alerts.append(f"Disk usage high: {metrics['disk_percent']}%")
        
    # Determine overall health: CRITICAL if any alert, OK otherwise
    status = 'CRITICAL'if alerts else 'OK'
    return status, alerts

# Main execution: collect, check, output JSON
def main():
    args = parse_args()
    
    metrics = collect_metrics()
    status, alerts = check_health(metrics, args)
    
    # structure output as json for easy consumption by monitoring systems
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'metrics': metrics,
        'alerts': alerts
    }

    # pretty print to stdout
    print(json.dumps(output, indent=2))
    
    # exit with non-zero code if critical (enables alertining in monitoring systems)
    sys.exit(1 if status == 'CRITICAL' else 0)
    
if __name__ == '__main__':
    main()