import subprocess
import platform
from loguru import logger

def check_gpu_devices():
    """Check available GPU devices and their capabilities"""
    gpu_info = {
        'intel': False,
        'nvidia': False,
        'devices': []
    }
    
    try:
        # Check Intel GPU
        intel_cmd = 'vainfo' if platform.system() != 'Windows' else 'where intel_gpu_top'
        intel_result = subprocess.run(intel_cmd, shell=True, capture_output=True, text=True)
        if intel_result.returncode == 0:
            gpu_info['intel'] = True
            gpu_info['devices'].append('Intel GPU (VA-API supported)')
            logger.info("Intel GPU with VA-API support detected")
            
        # Check NVIDIA GPU
        nvidia_cmd = 'nvidia-smi' if platform.system() != 'Windows' else 'where nvidia-smi'
        nvidia_result = subprocess.run(nvidia_cmd, shell=True, capture_output=True, text=True)
        if nvidia_result.returncode == 0:
            gpu_info['nvidia'] = True
            gpu_info['devices'].append('NVIDIA Quadro')
            logger.info("NVIDIA GPU detected")
            
    except Exception as e:
        logger.error(f"Error checking GPU devices: {e}")
    
    return gpu_info

def monitor_gpu_usage():
    """Monitor current GPU utilization"""
    try:
        if platform.system() == 'Windows':
            # Windows GPU monitoring
            nvidia_cmd = 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader'
            intel_cmd = 'intel_gpu_top -J'  # JSON output format
        else:
            # Linux GPU monitoring
            nvidia_cmd = 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader'
            intel_cmd = 'intel_gpu_top -s 1 -o -'
            
        usage = {}
        
        # Check NVIDIA GPU usage
        try:
            nvidia_output = subprocess.check_output(nvidia_cmd, shell=True, text=True)
            usage['nvidia'] = float(nvidia_output.strip())
            logger.info(f"NVIDIA GPU Utilization: {usage['nvidia']}%")
        except:
            usage['nvidia'] = 0
            
        # Check Intel GPU usage
        try:
            intel_output = subprocess.check_output(intel_cmd, shell=True, text=True)
            if platform.system() == 'Windows':
                import json
                usage['intel'] = json.loads(intel_output)['engines']['render']['busy']
            else:
                usage['intel'] = float(intel_output.split()[0])
            logger.info(f"Intel GPU Utilization: {usage['intel']}%")
        except:
            usage['intel'] = 0
            
        return usage
        
    except Exception as e:
        logger.error(f"Error monitoring GPU usage: {e}")
        return None
