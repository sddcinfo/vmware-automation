import os
import subprocess
import sys
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


def run_command(command, description):
    """Runs a command and returns its stdout. Exits on error."""
    print(f"[ACTION] {description}...")
    try:
        process = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"[SUCCESS] {description} complete.")
        if process.stdout.strip(): print(f"  [STDOUT] {process.stdout.strip()}")
        if process.stderr.strip(): print(f"  [STDERR] {process.stderr.strip()}")
        return process.stdout
    except FileNotFoundError:
        print(f"\n[ERROR] Command not found: '{command[0]}'. Please check the path.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Failed to {description.lower()}.", file=sys.stderr)
        print(f"  - Command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"  - Return Code: {e.returncode}", file=sys.stderr)
        print(f"  - STDOUT: {e.stdout.strip()}", file=sys.stderr)
        print(f"  - STDERR: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def reconfigure_vmx(vmx_path, installer_iso_path, cidata_iso_path):
    """Reconfigures the VMX to attach the installer and cidata ISOs."""
    print(f"[ACTION] Reconfiguring VMX file at {vmx_path}...")
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
        print("[SUCCESS] VMX file reconfigured.")
    except Exception as e:
        print(f"\n[ERROR] Failed to reconfigure VMX file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to orchestrate the automated creation of an Ubuntu VM."""
    print("--- Starting Cloud-Init Based VM Creation ---")

    # 1. Create the cidata.iso for cloud-init
    cidata_script = os.path.join(SCRIPT_DIR, "create-cidata-iso.py")
    run_command([sys.executable, cidata_script], "Create cidata.iso")

    # 2. Check for required files
    if not all([os.path.exists(VMRUN_PATH), os.path.exists(ORIGINAL_ISO_PATH), os.path.exists(TEMPLATE_VMX_PATH)]):
        print("\n[ERROR] A required file or directory was not found. Check config.py.", file=sys.stderr)
        sys.exit(1)

    # 3. Clean up previous VM
    if os.path.exists(NEW_VM_PATH):
        print(f"[INFO] Previous VM '{NEW_VM_PATH}' exists. Running cleanup...")
        cleanup_script = os.path.join(SCRIPT_DIR, "cleanup.py")
        run_command([sys.executable, cleanup_script, NEW_VMX_PATH], "Run cleanup script")

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
    
    print("\n--- SCRIPT FINISHED ---")
    print("The VM has been cloned and started with the cidata ISO for automated installation.")


if __name__ == "__main__":
    main()
