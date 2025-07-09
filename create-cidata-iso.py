import os
import pycdlib

def create_cidata_iso(script_dir):
    """
    Creates a cidata.iso file containing user-data and meta-data
    for cloud-init.
    """
    autoinstall_dir = os.path.join(script_dir, 'autoinstall')
    output_iso_path = os.path.join(script_dir, 'cidata.iso')
    user_data_path = os.path.join(autoinstall_dir, 'user-data')
    meta_data_path = os.path.join(autoinstall_dir, 'meta-data')

    if not all([os.path.exists(user_data_path), os.path.exists(meta_data_path)]):
        print(f"[ERROR] user-data or meta-data not found in {autoinstall_dir}")
        return False

    iso = pycdlib.PyCdlib()
    iso.new(vol_ident='cidata',
            joliet=True,
            rock_ridge='1.12')

    # Add the files to the root of the ISO
    iso.add_file(user_data_path, '/USERDATA.;1', joliet_path='/user-data', rr_name='user-data')
    iso.add_file(meta_data_path, '/METADATA.;1', joliet_path='/meta-data', rr_name='meta-data')

    iso.write(output_iso_path)
    iso.close()
    print(f"[SUCCESS] Created cidata.iso at {output_iso_path}")
    return True

if __name__ == '__main__':
    """
    This allows the script to be run directly for testing or manual ISO creation.
    """
    create_cidata_iso(os.path.dirname(os.path.abspath(__file__)))
