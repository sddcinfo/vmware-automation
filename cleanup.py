import os
import shutil
import sys
import time
import subprocess
from config import (
    VMRUN_PATH,
    NEW_VM_NAME as DEFAULT_VM_NAME,
    VM_BASE_PATH as DEFAULT_VM_BASE_PATH,
)

def main(vmx_to_delete):
    """
    Stops and deletes the virtual machine specified by the VMX file path.
    """
    print("--- Starting Robust Cleanup Process ---")

    if not os.path.exists(vmx_to_delete):
        print(f"[INFO] VMX file not found at '{vmx_to_delete}'. Nothing to clean up.")
        return

    vm_path = os.path.dirname(vmx_to_delete)
    
    print(f"[INFO] Found VM at {vmx_to_delete}.")
    print(f"[ACTION] Attempting to forcefully power off VM to release file locks...")
    subprocess.run([VMRUN_PATH, "stop", vmx_to_delete, "hard"], capture_output=True)
    print("[SUCCESS] VM power-off command issued.")
    
    print("[INFO] Waiting 5 seconds for file locks to release...")
    time.sleep(5)

    print(f"[ACTION] Deleting entire VM folder: {vm_path}")
    try:
        shutil.rmtree(vm_path)
        print("[SUCCESS] VM folder completely removed.")
    except OSError as e:
        print(f"[ERROR] Could not delete VM folder: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- Cleanup Finished ---")

if __name__ == '__main__':
    # This script can be run with an argument, or it will use the default.
    if len(sys.argv) == 2:
        # Use the VMX path provided as a command-line argument
        vmx_file_path = sys.argv[1]
    elif len(sys.argv) == 1:
        # Use the default VMX path from the configuration
        vm_path = os.path.join(DEFAULT_VM_BASE_PATH, DEFAULT_VM_NAME)
        vmx_file_path = os.path.join(vm_path, f"{DEFAULT_VM_NAME}.vmx")
    else:
        print("Usage: python cleanup.py [<path_to_vmx_file>]", file=sys.stderr)
        sys.exit(1)
    
    main(vmx_file_path)
