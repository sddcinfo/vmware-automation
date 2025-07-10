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
    """
    Reconfigures the VMX file by appending settings. This is safer than
    rewriting the file, as it preserves original encoding and metadata.
    """
    print(f"[ACTION] Reconfiguring VMX file at {vmx_path}...")
    installer_iso_vmx = installer_iso_path.replace('', '/')
    cidata_iso_vmx = cidata_iso_path.replace('', '/')
    
    # Settings to add. We will append these to the VMX file.
    settings_to_add = {
        "bios.bootOrder": '"cdrom"',
        "guestinfo.autoinstall.interactive": '"false"',
        "sata0:0.present": '"TRUE"',
        "sata0:0.fileName": f'"{installer_iso_vmx}"',
        "sata0:0.deviceType": '"cdrom-image"',
        "sata0:0.startConnected": '"TRUE"',
        "sata0:1.present": '"TRUE"',
        "sata0:1.fileName": f'"{cidata_iso_vmx}"',
        "sata0:1.deviceType": '"cdrom-image"',
        "sata0:1.startConnected": '"TRUE"',
    }

    try:
        # Read all lines, preserving encoding. utf-8-sig handles BOMs.
        with open(vmx_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # Create a dictionary of keys to remove for efficient lookup
        keys_to_remove = {k.split('.')[0] for k in settings_to_add.keys()}
        keys_to_remove.add('floppy') # Also remove floppy devices
        # Add additional keys found in corrected_old_string that were not in original_old_string
        keys_to_remove.add('bios')
        keys_to_remove.add('virtualHW')
        keys_to_remove.add('guestOS')
        keys_to_remove.add('scsi0')

        # Filter out lines containing keys we intend to replace/add.
        # This prevents duplicate or conflicting settings.
        filtered_lines = [
            line for line in lines 
            if line.strip().split('.')[0] not in keys_to_remove
        ]

        # Append the new settings to the filtered list.
        for key, value in settings_to_add.items():
            filtered_lines.append(f'{key} = {value}\n')

        # Write the modified content back, preserving encoding.
        with open(vmx_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(filtered_lines)
            
        print("[SUCCESS] VMX file reconfigured using append method.")
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
