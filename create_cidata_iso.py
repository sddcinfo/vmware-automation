"""Cloud-init ISO creation module.

This module creates ISO images containing cloud-init configuration data
for automated Ubuntu VM provisioning using the cidata standard.
"""

import os
import logging
from pathlib import Path
from typing import bool

import pycdlib

from config import CIDATA_ISO_PATH, SCRIPT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_cidata_iso() -> bool:
    """Create cloud-init data ISO for automated VM provisioning.
    
    Creates an ISO image with volume ID 'cidata' containing user-data and
    meta-data files required for cloud-init automated installation.
    
    The ISO uses both Joliet and Rock Ridge extensions for maximum
    compatibility across different systems.
    
    Returns:
        bool: True if ISO creation successful, False otherwise
        
    Raises:
        Exception: On ISO creation or file operation failure
    """
    logger.info("Starting cloud-init ISO creation")
    
    # Define paths for autoinstall configuration files
    autoinstall_dir = Path(SCRIPT_DIR) / 'autoinstall'
    user_data_path = autoinstall_dir / 'user-data'
    meta_data_path = autoinstall_dir / 'meta-data'
    
    # Validate required files exist
    required_files = {
        'user-data': user_data_path,
        'meta-data': meta_data_path
    }
    
    missing_files = [name for name, path in required_files.items() if not path.exists()]
    if missing_files:
        logger.error(f"Required cloud-init files not found: {', '.join(missing_files)}")
        logger.error(f"Expected location: {autoinstall_dir}")
        return False
    
    logger.info(f"Found required files in {autoinstall_dir}")

    # Remove existing ISO if present
    cidata_path = Path(CIDATA_ISO_PATH)
    if cidata_path.exists():
        cidata_path.unlink()
        logger.info(f"Removed existing cidata.iso at {CIDATA_ISO_PATH}")

    try:
        # Create new ISO with cloud-init data
        logger.info("Creating new cidata ISO with cloud-init configuration")
        iso = pycdlib.PyCdlib()
        iso.new(
            vol_ident='cidata',
            joliet=True,
            rock_ridge='1.12'
        )

        # Add cloud-init files to ISO root with proper naming
        iso.add_file(
            str(user_data_path), 
            '/USERDATA.;1', 
            joliet_path='/user-data', 
            rr_name='user-data'
        )
        iso.add_file(
            str(meta_data_path), 
            '/METADATA.;1', 
            joliet_path='/meta-data', 
            rr_name='meta-data'
        )

        # Write ISO to disk and cleanup
        iso.write(CIDATA_ISO_PATH)
        iso.close()
        
        logger.info(f"Successfully created cidata.iso at {CIDATA_ISO_PATH}")
        logger.info(f"ISO contains: user-data ({user_data_path.stat().st_size} bytes), meta-data ({meta_data_path.stat().st_size} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create cidata.iso: {e}")
        return False

if __name__ == '__main__':
    """Command-line interface for cloud-init ISO creation.
    
    This allows the script to be run independently for testing or
    manual ISO creation outside of the main VM creation workflow.
    """
    logger.info("Running cidata ISO creation in standalone mode")
    success = create_cidata_iso()
    
    if success:
        logger.info("Standalone ISO creation completed successfully")
    else:
        logger.error("Standalone ISO creation failed")
        exit(1)
