# VMware Workstation Automation for Ubuntu 24.04

This project provides a set of Python scripts to fully automate the creation of an Ubuntu 24.04 virtual machine in VMware Workstation using cloud-init for unattended installation.

## Features

- **Fully Automated**: Creates a new Ubuntu VM from a template with zero manual intervention.
- **Cloud-Init Driven**: Uses a `cidata.iso` with `user-data` and `meta-data` for robust, unattended OS installation and configuration.
- **Clean and Modular**: Scripts are separated by concern (VM creation, ISO creation, cleanup).
- **Robust**: Includes error handling and cleanup logic to manage existing VMs.

## Prerequisites

1.  **VMware Workstation**: Must be installed on the host machine. The automation relies on the `vmrun.exe` command-line utility that is included with the installation.
2.  **Python 3**: With `pip` available.
3.  **Ubuntu 24.04 Server ISO**: You must download the installer ISO from the official Ubuntu website.
4.  **Template VM**: A base Ubuntu VM must be created in VMware Workstation. This can be a minimal installation or even a blank VM with the correct OS type set. This template will be cloned to create new VMs.

## Creating the Ubuntu Template VM

The automation relies on cloning a base template VM. It is crucial that this template is a **blank VM** with the correct hardware configuration, but **without an operating system installed**. The scripts will handle the OS installation automatically.

Follow these steps to create the template:

1.  **Open VMware Workstation** and select **File > New Virtual Machine**.
2.  Choose **Typical (recommended)** and click Next.
3.  Select **I will install the operating system later.** and click Next. This is the most important step.
4.  For the Guest operating system, select **Linux**. For the Version, select **Ubuntu 64-bit**. Click Next.
5.  Name the virtual machine **ubuntu-template**. You can store it in your default VM directory. Click Next.
6.  Specify a disk size of at least **25 GB**. Select **Store virtual disk as a single file** for better performance. Click Next.
7.  Click **Customize Hardware...** and configure the following:
    - **Memory**: Assign at least **4 GB** of memory.
    - **Processors**: Assign at least **2 processor cores**.
    - **Network Adapter**: Ensure it is set to **NAT** or **Bridged** to allow internet access for the installer.
8.  Click **Close**, then **Finish** to create the virtual machine.
9.  **Do not power on the VM.** The template is now ready. Make sure the path to its `.vmx` file is correctly set in `config.py`.

## Setup

1.  **Clone this repository.**
2.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure `config.py`**:
    Open `config.py` and edit the variables to match your environment:
    - `VMWARE_INSTALL_DIR`: The path to your VMware Workstation installation directory.
    - `VM_BASE_PATH`: The directory where new VMs will be created.
    - `TEMPLATE_VMX_PATH`: The absolute path to the `.vmx` file of your template VM.
    - `ORIGINAL_ISO_PATH`: The absolute path to your downloaded Ubuntu 24.04 Server ISO file.
    - `NEW_VM_NAME`: The desired name for the new virtual machine.

4.  **Configure Autoinstall**:
    - Open `autoinstall/user-data` and replace the placeholder SSH key with your own public SSH key.
    - You can also change the `hostname` and `username` in this file.
    - **Note on BIOS vs. UEFI**: The provided `user-data` file is configured for a template VM that uses legacy BIOS. If your template VM is configured to use UEFI, you will need to modify the `storage` section in `autoinstall/user-data` accordingly (e.g., by creating an EFI system partition).

## Usage

To create a new Ubuntu VM, simply run the main script:

```bash
python create-vm.py
```

The script will:
1.  Create a `cidata.iso` file containing your cloud-init configuration.
2.  Clean up any VM from a previous run.
3.  Clone your template VM.
4.  Attach the Ubuntu installer ISO and the `cidata.iso`.
5.  Set the VM to boot from the CD-ROM and start it, beginning the unattended installation.

## How It Works

The automation relies on the `cloud-init` standard, which is widely used for provisioning cloud instances. The Ubuntu installer (Subiquity) supports using a cloud-init data source for unattended installations.

This project uses the **cidata ISO method**. A small ISO image with the volume ID `cidata` is created, containing the `user-data` and `meta-data` files. When the Ubuntu installer boots, it automatically detects this ISO, reads the configuration, and proceeds with the installation without requiring any user input. This method is more reliable in VMware Workstation than using the `guestinfo` interface.
