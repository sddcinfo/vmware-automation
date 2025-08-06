"""VM cleanup utilities module.

This module provides functionality to safely stop and remove VMware VMs,
handling file locks and ensuring complete cleanup of VM resources.
"""

import os
import shutil
import sys
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional

from config import (
    VMRUN_PATH,
    NEW_VM_NAME as DEFAULT_VM_NAME,
    VM_BASE_PATH as DEFAULT_VM_BASE_PATH,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(vmx_to_delete: str) -> None:
    """Stop and delete a VMware virtual machine completely.
    
    This function performs a complete cleanup of a VM including:
    1. Forceful shutdown of running VM
    2. Waiting for file lock release
    3. Complete removal of VM directory and files
    
    Args:
        vmx_to_delete: Path to the VMX file of the VM to delete
        
    Raises:
        SystemExit: On cleanup failure
    """
    logger.info("Starting VM cleanup process")

    if not os.path.exists(vmx_to_delete):
        logger.info(f"VMX file not found at '{vmx_to_delete}' - nothing to clean up")
        return

    vm_path = os.path.dirname(vmx_to_delete)
    
    logger.info(f"Found VM to clean up: {vmx_to_delete}")
    logger.info("Attempting to forcefully shutdown VM")
    
    # Try to stop the VM gracefully first, then hard stop if needed
    try:
        subprocess.run(
            [VMRUN_PATH, "stop", vmx_to_delete, "soft"], 
            capture_output=True, 
            timeout=30,
            check=True
        )
        logger.info("VM stopped gracefully")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        logger.warning("Graceful shutdown failed, forcing hard stop")
        subprocess.run(
            [VMRUN_PATH, "stop", vmx_to_delete, "hard"], 
            capture_output=True
        )
        logger.info("VM force-stopped")
    
    logger.info("Waiting for file locks to release (5 seconds)")
    time.sleep(5)

    logger.info(f"Removing VM directory: {vm_path}")
    try:
        shutil.rmtree(vm_path)
        logger.info("VM directory successfully removed")
    except OSError as e:
        logger.error(f"Failed to delete VM directory: {e}")
        sys.exit(1)

    logger.info("VM cleanup completed successfully")

if __name__ == '__main__':
    """Command-line interface for VM cleanup.
    
    Usage:
        python cleanup.py                    # Clean default VM
        python cleanup.py <path_to_vmx>     # Clean specific VM
    """
    if len(sys.argv) == 2:
        # Clean specific VM by VMX path
        vmx_file_path = sys.argv[1]
        logger.info(f"Cleaning VM specified by path: {vmx_file_path}")
    elif len(sys.argv) == 1:
        # Clean default VM from configuration
        vm_path = os.path.join(DEFAULT_VM_BASE_PATH, DEFAULT_VM_NAME)
        vmx_file_path = os.path.join(vm_path, f"{DEFAULT_VM_NAME}.vmx")
        logger.info(f"Cleaning default VM: {vmx_file_path}")
    else:
        logger.error("Invalid arguments")
        logger.error("Usage: python cleanup.py [<path_to_vmx_file>]")
        sys.exit(1)
    
    main(vmx_file_path)
