import os
import shutil
import sys
import pycdlib
from config import (
    ORIGINAL_ISO_PATH,
    CUSTOM_ISO_PATH,
    TEMP_ISO_DIR as TEMP_DIR,
)

def main():
    """
    Creates a customized, bootable Ubuntu installer ISO that contains the
    'autoinstall' kernel parameter by default.
    """
    print("--- Starting Custom ISO Preparation ---")

    # 1. Clean up any previous temporary directories
    if os.path.exists(TEMP_DIR):
        print(f"[INFO] Removing previous temporary directory: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    print(f"[SUCCESS] Created temporary directory: {TEMP_DIR}")

    # 2. Extract the original ISO
    print(f"[ACTION] Extracting original ISO: {ORIGINAL_ISO_PATH}...")
    try:
        iso = pycdlib.PyCdlib()
        iso.open(ORIGINAL_ISO_PATH)
        for dirname, _, filelist in iso.walk(iso_path='/'):
            # Create the directory structure on the local filesystem
            local_dir_path = os.path.join(TEMP_DIR, dirname.strip('/'))
            os.makedirs(local_dir_path, exist_ok=True)
            
            for filename in filelist:
                local_file_path = os.path.join(local_dir_path, filename)
                iso.get_file_from_iso(local_file_path, iso_path=os.path.join(dirname, filename))
        iso.close()
        print("[SUCCESS] ISO extracted successfully.")
    except Exception as e:
        print(f"\n[ERROR] Failed to extract ISO: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Modify the boot configuration
    print("[ACTION] Modifying boot configuration...")
    grub_cfg_path = os.path.join(TEMP_DIR, 'boot', 'grub', 'grub.cfg')
    if not os.path.exists(grub_cfg_path):
        print(f"\n[ERROR] grub.cfg not found at {grub_cfg_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(grub_cfg_path, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            # Find the default boot entry's kernel line
            if line.strip().startswith('linux'):
                # Add 'autoinstall' before the '---'
                line = line.replace('---', 'autoinstall ---')
                print("[INFO] Found and modified kernel boot line.")
            new_lines.append(line)
            
        with open(grub_cfg_path, 'w') as f:
            f.writelines(new_lines)
        print("[SUCCESS] Boot configuration modified.")
    except Exception as e:
        print(f"\n[ERROR] Failed to modify grub.cfg: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Re-master the ISO
    print(f"[ACTION] Re-mastering new ISO at {CUSTOM_ISO_PATH}...")
    try:
        new_iso = pycdlib.PyCdlib()
        new_iso.new(joliet=True, rock_ridge='1.12')
        
        # Add all the extracted and modified files to the new ISO
        new_iso.add_directory(TEMP_DIR, iso_path='/')
        
        # Make the ISO bootable
        new_iso.add_boot_info(b'eltorito', b'boot/grub/i386-pc/eltorito.img')
        
        new_iso.write(CUSTOM_ISO_PATH)
        new_iso.close()
        print("[SUCCESS] New bootable ISO created.")
    except Exception as e:
        print(f"\n[ERROR] Failed to re-master ISO: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 5. Clean up the temporary directory
    print(f"[ACTION] Cleaning up temporary directory: {TEMP_DIR}")
    shutil.rmtree(TEMP_DIR)
    print("[SUCCESS] Cleanup complete.")

    print("\n--- Custom ISO Preparation Finished ---")


if __name__ == '__main__':
    main()
