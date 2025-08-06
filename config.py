"""Configuration module for VMware automation.

This module contains all configuration settings for VMware Workstation
automation including paths, VM settings, and ISO locations.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging for configuration module
logger = logging.getLogger(__name__)

# --- VMware Configuration ---
# IMPORTANT: Set this to the installation directory of VMware Workstation
VMWARE_INSTALL_DIR = r"C:\Program Files (x86)\VMware\VMware Workstation"

# --- VM Configuration ---
# IMPORTANT: Set this to the base directory where you want to store your VMs
VM_BASE_PATH = r"D:\VMs"

# IMPORTANT: Set this to the full path of your template's .vmx file
TEMPLATE_VMX_PATH = os.path.join(VM_BASE_PATH, "ubuntu-template", "ubuntu-template.vmx")

# The name for the new VM
NEW_VM_NAME = "ubuntu-autoinstall-final"

# --- ISO Configuration ---
# IMPORTANT: Set this to the full path of the original Ubuntu Server ISO
ORIGINAL_ISO_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "ubuntu-24.04.2-live-server-amd64.iso")

# --- Script Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VMRUN_PATH = os.path.join(VMWARE_INSTALL_DIR, "vmrun.exe")
CUSTOM_ISO_PATH = os.path.join(SCRIPT_DIR, "ubuntu-autoinstall.iso")
CIDATA_ISO_PATH = os.path.join(SCRIPT_DIR, "cidata.iso")
NEW_VM_PATH = os.path.join(VM_BASE_PATH, NEW_VM_NAME)
NEW_VMX_PATH = os.path.join(NEW_VM_PATH, f"{NEW_VM_NAME}.vmx")
TEMP_ISO_DIR = os.path.join(SCRIPT_DIR, "iso_temp")


def validate_configuration() -> Dict[str, Any]:
    """Validate all configuration settings and return validation results.
    
    Returns:
        Dict containing validation results with 'valid' boolean and 'errors' list
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check VMware installation
    if not Path(VMWARE_INSTALL_DIR).exists():
        validation_result['errors'].append(
            f"VMware installation directory not found: {VMWARE_INSTALL_DIR}"
        )
        validation_result['valid'] = False
    
    if not Path(VMRUN_PATH).exists():
        validation_result['errors'].append(
            f"vmrun.exe not found: {VMRUN_PATH}"
        )
        validation_result['valid'] = False
    
    # Check VM base path
    vm_base = Path(VM_BASE_PATH)
    if not vm_base.exists():
        validation_result['warnings'].append(
            f"VM base directory will be created: {VM_BASE_PATH}"
        )
    elif not vm_base.is_dir():
        validation_result['errors'].append(
            f"VM base path exists but is not a directory: {VM_BASE_PATH}"
        )
        validation_result['valid'] = False
    
    # Check template VM
    template_path = Path(TEMPLATE_VMX_PATH)
    if not template_path.exists():
        validation_result['errors'].append(
            f"Template VMX file not found: {TEMPLATE_VMX_PATH}"
        )
        validation_result['valid'] = False
    elif not template_path.is_file():
        validation_result['errors'].append(
            f"Template VMX path exists but is not a file: {TEMPLATE_VMX_PATH}"
        )
        validation_result['valid'] = False
    
    # Check Ubuntu ISO
    iso_path = Path(ORIGINAL_ISO_PATH)
    if not iso_path.exists():
        validation_result['errors'].append(
            f"Ubuntu ISO file not found: {ORIGINAL_ISO_PATH}"
        )
        validation_result['valid'] = False
    elif not iso_path.is_file():
        validation_result['errors'].append(
            f"Ubuntu ISO path exists but is not a file: {ORIGINAL_ISO_PATH}"
        )
        validation_result['valid'] = False
    elif iso_path.stat().st_size < 1024 * 1024 * 100:  # Less than 100MB
        validation_result['warnings'].append(
            f"Ubuntu ISO seems unusually small ({iso_path.stat().st_size / 1024 / 1024:.1f}MB): {ORIGINAL_ISO_PATH}"
        )
    
    # Check autoinstall directory
    autoinstall_dir = Path(SCRIPT_DIR) / 'autoinstall'
    if not autoinstall_dir.exists():
        validation_result['errors'].append(
            f"Autoinstall directory not found: {autoinstall_dir}"
        )
        validation_result['valid'] = False
    else:
        # Check for required autoinstall files
        user_data = autoinstall_dir / 'user-data'
        meta_data = autoinstall_dir / 'meta-data'
        
        if not user_data.exists():
            validation_result['errors'].append(
                f"user-data file not found: {user_data}"
            )
            validation_result['valid'] = False
        
        if not meta_data.exists():
            validation_result['errors'].append(
                f"meta-data file not found: {meta_data}"
            )
            validation_result['valid'] = False
    
    # Validate VM name
    if not NEW_VM_NAME or not NEW_VM_NAME.strip():
        validation_result['errors'].append("VM name cannot be empty")
        validation_result['valid'] = False
    elif any(char in NEW_VM_NAME for char in '<>:"/\\|?*'):
        validation_result['errors'].append(
            f"VM name contains invalid characters: {NEW_VM_NAME}"
        )
        validation_result['valid'] = False
    
    return validation_result


def get_configuration_summary() -> str:
    """Get a formatted summary of current configuration settings.
    
    Returns:
        Formatted string with configuration details
    """
    return f"""VMware Automation Configuration Summary:
    
    VMware Settings:
      Installation Directory: {VMWARE_INSTALL_DIR}
      vmrun Path: {VMRUN_PATH}
    
    VM Configuration:
      Base Path: {VM_BASE_PATH}
      Template VMX: {TEMPLATE_VMX_PATH}
      New VM Name: {NEW_VM_NAME}
    
    ISO Settings:
      Ubuntu ISO: {ORIGINAL_ISO_PATH}
      Cloud-Init ISO: {CIDATA_ISO_PATH}
    
    Script Directories:
      Script Directory: {SCRIPT_DIR}
      Autoinstall Directory: {os.path.join(SCRIPT_DIR, 'autoinstall')}
    """


if __name__ == "__main__":
    """Configuration validation when run directly."""
    print(get_configuration_summary())
    print("\n" + "="*50)
    print("Configuration Validation Results:")
    print("="*50)
    
    results = validate_configuration()
    
    if results['warnings']:
        print("\nWarnings:")
        for warning in results['warnings']:
            print(f"  [WARNING] {warning}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  [ERROR] {error}")
    
    if results['valid']:
        print("\n[SUCCESS] Configuration is valid!")
    else:
        print("\n[FAILED] Configuration has errors that must be fixed.")
        exit(1)
