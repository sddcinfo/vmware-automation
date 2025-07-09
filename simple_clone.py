import os
import subprocess
import sys
import shutil
from config import (
    VMWARE_INSTALL_DIR,
    TEMPLATE_VMX_PATH,
    NEW_VM_NAME,
    VM_BASE_PATH,
)

# --- Global Paths ---
VMRUN_EXE = "vmrun.exe"
NEW_VM_PATH = os.path.join(VM_BASE_PATH, NEW_VM_NAME)
NEW_VMX_PATH = os.path.join(NEW_VM_PATH, f"{NEW_VM_NAME}.vmx")

def run_clone():
    """Runs only the vmrun clone command with a modified PATH."""
    print("--- Starting Simple Clone Test ---")

    # 1. Check for required files and directories
    if not os.path.isdir(VMWARE_INSTALL_DIR):
        print(f"[ERROR] VMware directory not found at: {VMWARE_INSTALL_DIR}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(TEMPLATE_VMX_PATH):
        print(f"[ERROR] Template VMX not found at: {TEMPLATE_VMX_PATH}", file=sys.stderr)
        sys.exit(1)

    # 2. Clean up previous test clone if it exists
    if os.path.exists(NEW_VM_PATH):
        print(f"[INFO] Deleting previous test clone at: {NEW_VM_PATH}")
        # A simple directory removal is enough for this test
        shutil.rmtree(NEW_VM_PATH)

    # 3. Prepare environment and command
    env = os.environ.copy()
    env['PATH'] = f"{VMWARE_INSTALL_DIR};{env['PATH']}"
    
    clone_command = [
        VMRUN_EXE, '-T', 'ws', 'clone', TEMPLATE_VMX_PATH, NEW_VMX_PATH, 'full', f'-cloneName={NEW_VM_NAME}'
    ]

    # 4. Execute the clone command
    print(f"[ACTION] Attempting to clone '{TEMPLATE_VMX_PATH}'...")
    try:
        process = subprocess.run(clone_command, check=True, text=True, capture_output=True, env=env)
        print("[SUCCESS] Clone command completed successfully.")
        if process.stdout.strip():
            print(f"  [STDOUT] {process.stdout.strip()}")
        if process.stderr.strip():
            print(f"  [STDERR] {process.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] The clone operation failed.", file=sys.stderr)
        print(f"  - Command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"  - Return Code: {e.returncode}", file=sys.stderr)
        print(f"  - STDOUT: {e.stdout.strip()}", file=sys.stderr)
        print(f"  - STDERR: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_clone()
