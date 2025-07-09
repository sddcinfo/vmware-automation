import os
import shutil
import sys
import time
import subprocess
from config import VMRUN_PATH

def cleanup_vm(vmx_path):
    """
    Stops and deletes the virtual machine specified by the VMX file path.
    """
    print("--- Starting Robust Cleanup Process ---")

    if not os.path.exists(vmx_path):
        print(f"[INFO] VMX file not found at '{vmx_path}'. Nothing to clean up.")
        return

    vm_folder = os.path.dirname(vmx_path)
    
    print(f"[INFO] Found VM at {vmx_path}.")
    print(f"[ACTION] Attempting to forcefully power off VM to release file locks...")
    # We don't check the result of this, as it will fail if the VM is already off.
    subprocess.run([VMRUN_PATH, "stop", vmx_path, "hard"], capture_output=True)
    print("[SUCCESS] VM power-off command issued.")
    
    # Give the OS a moment to release file handles
    print("[INFO] Waiting 3 seconds for file locks to release...")
    time.sleep(3)

    print(f"[ACTION] Deleting entire VM folder: {vm_folder}")
    try:
        shutil.rmtree(vm_folder)
        print("[SUCCESS] VM folder completely removed.")
    except OSError as e:
        print(f"[ERROR] Could not delete VM folder: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- Cleanup Finished ---")

if __name__ == '__main__':
    from config import NEW_VM_NAME, VM_BASE_PATH
    # This allows the script to be run directly for testing.
    if len(sys.argv) == 2:
        vmx_file_path = sys.argv[1]
    elif len(sys.argv) == 1:
        vm_path = os.path.join(VM_BASE_PATH, NEW_VM_NAME)
        vmx_file_path = os.path.join(vm_path, f"{NEW_VM_NAME}.vmx")
    else:
        print("Usage: python cleanup.py [<path_to_vmx_file>]", file=sys.stderr)
        sys.exit(1)
    
    cleanup_vm(vmx_file_path)
