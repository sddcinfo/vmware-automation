import os

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
