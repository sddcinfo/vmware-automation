import os
import sys
import pycdlib
from config import CIDATA_ISO_PATH, SCRIPT_DIR

def create_cidata_iso():
    """
    Creates a cidata.iso file containing user-data and meta-data
    for cloud-init, using paths from the config file.
    """
    print("[ACTION] Creating cidata.iso...")
    autoinstall_dir = os.path.join(SCRIPT_DIR, 'autoinstall')
    user_data_path = os.path.join(autoinstall_dir, 'user-data')
    meta_data_path = os.path.join(autoinstall_dir, 'meta-data')

    if not all([os.path.exists(user_data_path), os.path.exists(meta_data_path)]):
        print(f"[ERROR] user-data or meta-data not found in {autoinstall_dir}", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(CIDATA_ISO_PATH):
        print(f"[INFO] Removing existing cidata.iso at {CIDATA_ISO_PATH}")
        os.remove(CIDATA_ISO_PATH)

    try:
        iso = pycdlib.PyCdlib()
        iso.new(vol_ident='cidata', joliet=True, rock_ridge='1.12')
        iso.add_file(user_data_path, '/USERDATA.;1', joliet_path='/user-data', rr_name='user-data')
        iso.add_file(meta_data_path, '/METADATA.;1', joliet_path='/meta-data', rr_name='meta-data')
        iso.write(CIDATA_ISO_PATH)
        iso.close()
        print(f"[SUCCESS] Created cidata.iso at {CIDATA_ISO_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to create cidata.iso: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    """
    This allows the script to be run directly for testing or manual ISO creation.
    """
    create_cidata_iso()
