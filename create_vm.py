"""Main VM creation orchestration module.

This module handles the complete workflow for creating Ubuntu VMs in VMware
Workstation using cloud-init for automated installation.
"""

import os
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from config import (
    VMRUN_PATH,
    ORIGINAL_ISO_PATH,
    TEMPLATE_VMX_PATH,
    NEW_VM_NAME,
    NEW_VM_PATH,
    NEW_VMX_PATH,
    CIDATA_ISO_PATH,
    SCRIPT_DIR,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('vmware_automation.log')
    ]
)
logger = logging.getLogger(__name__)


def run_command(command: List[str], description: str) -> str:
    """Execute a system command with comprehensive error handling.
    
    Args:
        command: List of command components to execute
        description: Human-readable description of the operation
        
    Returns:
        Command stdout as string
        
    Raises:
        SystemExit: On command failure or file not found
    """
    logger.info(f"Starting: {description}")
    try:
        process = subprocess.run(
            command, 
            check=True, 
            text=True, 
            capture_output=True,
            timeout=300  # 5 minute timeout
        )
        logger.info(f"Successfully completed: {description}")
        if process.stdout.strip(): 
            logger.debug(f"STDOUT: {process.stdout.strip()}")
        if process.stderr.strip(): 
            logger.warning(f"STDERR: {process.stderr.strip()}")
        return process.stdout
    except FileNotFoundError:
        logger.error(f"Command not found: '{command[0]}'. Please check the path.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {description}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to {description.lower()}")
        logger.error(f"Command: {' '.join(e.cmd)}")
        logger.error(f"Return Code: {e.returncode}")
        logger.error(f"STDOUT: {e.stdout.strip()}")
        logger.error(f"STDERR: {e.stderr.strip()}")
        sys.exit(1)

def reconfigure_vmx(vmx_path: str, installer_iso_path: str, cidata_iso_path: str) -> None:
    """Reconfigure VMX file to attach installer and cloud-init ISOs.
    
    Args:
        vmx_path: Path to the VMX file to modify
        installer_iso_path: Path to Ubuntu installer ISO
        cidata_iso_path: Path to cloud-init data ISO
        
    Raises:
        SystemExit: On file operation failure
    """
    logger.info(f"Reconfiguring VMX file: {vmx_path}")
    installer_iso_vmx = installer_iso_path.replace('\\', '/')
    cidata_iso_vmx = cidata_iso_path.replace('\\', '/')
    
    new_settings = [
        'bios.bootOrder = "cdrom"',
        'sata0:0.present = "TRUE"',
        f'sata0:0.fileName = "{installer_iso_vmx}"',
        'sata0:0.deviceType = "cdrom-image"',
        'sata0:0.startConnected = "TRUE"',
        'sata0:1.present = "TRUE"',
        f'sata0:1.fileName = "{cidata_iso_vmx}"',
        'sata0:1.deviceType = "cdrom-image"',
        'sata0:1.startConnected = "TRUE"',
    ]
    
    try:
        with open(vmx_path, 'r') as f: lines = f.readlines()
        keys_to_remove = ['bios.bootOrder', 'guestinfo.', 'floppy', 'sata0:0.', 'sata0:1.']
        filtered_lines = [l for l in lines if not any(l.strip().startswith(k) for k in keys_to_remove)]
        final_lines = filtered_lines + ['\n'] + [f'{s}\n' for s in new_settings]
        with open(vmx_path, 'w') as f: f.writelines(final_lines)
        logger.info("VMX file successfully reconfigured")
    except Exception as e:
        logger.error(f"Failed to reconfigure VMX file: {e}")
        sys.exit(1)

def main() -> None:
    """Main orchestration function for automated Ubuntu VM creation.
    
    Coordinates the complete workflow:
    1. Create cloud-init ISO
    2. Validate required files
    3. Clean up previous VM instances
    4. Clone template VM
    5. Configure VM with ISOs
    6. Start automated installation
    """
    logger.info("Starting Cloud-Init Based VM Creation")

    # 1. Create the cidata.iso for cloud-init
    cidata_script = os.path.join(SCRIPT_DIR, "create_cidata_iso.py")
    run_command([sys.executable, cidata_script], "Create cidata.iso")

    # 2. Validate required files exist
    required_files = {
        "VMware vmrun.exe": VMRUN_PATH,
        "Ubuntu ISO": ORIGINAL_ISO_PATH,
        "Template VMX": TEMPLATE_VMX_PATH
    }
    
    missing_files = [name for name, path in required_files.items() if not os.path.exists(path)]
    if missing_files:
        logger.error(f"Required files not found: {', '.join(missing_files)}")
        logger.error("Please check your config.py configuration")
        sys.exit(1)
    
    logger.info("All required files validated successfully")

    # 3. Clean up any existing VM
    if os.path.exists(NEW_VM_PATH):
        logger.info(f"Found existing VM at {NEW_VM_PATH}, initiating cleanup")
        cleanup_script = os.path.join(SCRIPT_DIR, "cleanup.py")
        run_command([sys.executable, cleanup_script, NEW_VMX_PATH], "Clean up existing VM")

    # 4. Clone the VM
    clone_command = [
        VMRUN_PATH, '-T', 'ws', 'clone', TEMPLATE_VMX_PATH, NEW_VMX_PATH, 'full', f'-cloneName={NEW_VM_NAME}'
    ]
    run_command(clone_command, f"Clone '{NEW_VM_NAME}' from template")

    # 5. Reconfigure the new VMX file
    reconfigure_vmx(NEW_VMX_PATH, ORIGINAL_ISO_PATH, CIDATA_ISO_PATH)

    # 6. Start the new VM
    start_command = [VMRUN_PATH, 'start', NEW_VMX_PATH, 'gui']
    run_command(start_command, f"Start the '{NEW_VM_NAME}' VM")
    
    logger.info("VM Creation Completed Successfully")
    logger.info(f"VM '{NEW_VM_NAME}' has been created and started")
    logger.info("Automated Ubuntu installation is now in progress")
    logger.info(f"Monitor VM console in VMware Workstation for installation status")


if __name__ == "__main__":
    main()
