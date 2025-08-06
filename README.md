# VMware Workstation Ubuntu Automation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Professional automation suite for creating Ubuntu 24.04 virtual machines in VMware Workstation using cloud-init for unattended installation and configuration.

## ✨ Features

- **🤖 Fully Automated**: Zero-touch VM creation from template to running system
- **☁️ Cloud-Init Integration**: Industry-standard provisioning with `user-data` configuration  
- **🧹 Intelligent Cleanup**: Robust VM lifecycle management with cleanup utilities
- **🔧 Modular Design**: Separated concerns across dedicated Python modules
- **📋 Error Handling**: Comprehensive error reporting and recovery mechanisms
- **⚙️ Configurable**: Customizable network, storage, and package configurations

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/sddcinfo/vmware-automation.git
cd vmware-automation

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp config.py.example config.py
# Edit config.py with your specific paths

# Create your first VM
python create_vm.py
```

## 📋 Prerequisites

### Required Software
- **VMware Workstation** (tested on v16+) with vmrun.exe
- **Python 3.8+** with pip package manager
- **Ubuntu 24.04 Server ISO** ([download here](https://ubuntu.com/download/server))

### System Requirements  
- **Disk Space**: 25GB+ available for VM storage
- **Memory**: 4GB+ recommended for VM operation
- **Network**: Internet connection for package installation during VM setup

## ⚙️ Configuration

### Template VM Creation

Create a blank Ubuntu template VM in VMware Workstation:

1. **New Virtual Machine** → **Typical (recommended)**
2. **⚠️ CRITICAL**: Select "I will install the operating system later"
3. **Guest OS**: Linux → Ubuntu 64-bit  
4. **VM Name**: `ubuntu-template`
5. **Hardware Configuration**:
   - **Disk**: 25GB minimum (single file recommended)
   - **Memory**: 4GB+
   - **Processors**: 2+ cores
   - **Network**: NAT or Bridged for internet access

**Important**: Do not power on the template VM. The automation handles OS installation.

### Environment Setup

1. **Configure VMware Paths**: Update paths in `config.py`:
   - `VMWARE_INSTALL_DIR`: VMware Workstation installation directory
   - `VM_BASE_PATH`: Directory for storing VMs
   - `TEMPLATE_VMX_PATH`: Path to template VM's .vmx file
   - `ORIGINAL_ISO_PATH`: Ubuntu 24.04 Server ISO location
   - `NEW_VM_NAME`: Desired name for new VMs

2. **Cloud-Init Configuration**: Customize `autoinstall/user-data`:
   - **Hostname**: Change `ubuntu-vm` to your preferred hostname
   - **Username**: Modify default `sysadmin` username if desired
   - **Network**: Configure static IP or DHCP settings
   - **Packages**: Add/remove packages in the packages section
   - **Storage**: Configured for BIOS (modify for UEFI if needed)

## 🛠️ Usage

### Basic VM Creation
```bash
python create_vm.py
```

### Manual Components
```bash
# Create cloud-init ISO only
python create_cidata_iso.py

# Clean up specific VM  
python cleanup.py /path/to/vm.vmx

# Clean up default VM
python cleanup.py
```

### Automated Process
The script executes the following steps:
1. **🔧 Generate cidata.iso** with your cloud-init configuration
2. **🧹 Clean up** any existing VM from previous runs
3. **📋 Clone template** VM to create new instance
4. **💿 Attach ISOs** (Ubuntu installer + cidata for automation)
5. **🚀 Start VM** and begin unattended installation

**Note**: During installation, Ubuntu may prompt to confirm disk wiping - type `yes` to proceed. This is the only manual step required.

## 📁 Project Structure

```
vmware-automation/
├── config.py              # Configuration management with validation
├── create_vm.py           # Main orchestration script with logging
├── create_cidata_iso.py   # Cloud-init ISO generation
├── cleanup.py             # VM cleanup utilities  
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Modern Python packaging configuration
├── .gitignore             # Git ignore patterns
├── config.py.example      # Example configuration template
├── autoinstall/
│   ├── user-data         # Cloud-init configuration
│   └── meta-data         # Instance metadata
└── README.md             # This documentation
```

## 🔧 How It Works

This automation uses the **cloud-init standard** for VM provisioning:

- **Cloud-Init**: Industry standard for instance initialization
- **cidata ISO Method**: Creates ISO with volume ID `cidata` containing configuration
- **Ubuntu Autoinstall**: Subiquity installer automatically detects and uses cidata
- **VMware Integration**: Uses vmrun.exe for VM lifecycle management

The cidata ISO method is more reliable in VMware Workstation than guestinfo interfaces.

## 🔧 Advanced Configuration

### Network Configuration
Configure static IP in `autoinstall/user-data`:
```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: false
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
```

### Package Management
Add custom packages:
```yaml
packages:
  - git
  - docker.io
  - htop
  - vim
  - curl
```

### Post-Install Commands
Execute custom commands after installation:
```yaml
runcmd:
  - systemctl enable docker
  - usermod -aG docker sysadmin
  - apt update && apt upgrade -y
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Command not found: vmrun" | VMware path incorrect | Update `VMWARE_INSTALL_DIR` in config.py |
| "Template not found" | Missing template VM | Create template VM following setup guide |
| "ISO creation failed" | Missing autoinstall files | Verify `autoinstall/` directory exists |
| "VM won't start" | Hardware conflicts | Check VMware Workstation settings |
| "Network unreachable" | Network misconfiguration | Verify network settings in user-data |

### Debug Information
- Check VMware Workstation logs in VM directory
- Review cloud-init logs: `/var/log/cloud-init.log` in VM
- Verify ISO contents: Mount cidata.iso to inspect files

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/improvement`)  
3. **Commit** changes (`git commit -am 'Add feature'`)
4. **Push** to branch (`git push origin feature/improvement`)
5. **Create** Pull Request

Please ensure code follows project standards and includes appropriate documentation.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ubuntu Team** for comprehensive cloud-init documentation
- **VMware** for robust vmrun CLI automation tools  
- **Python Community** for pycdlib ISO creation library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sddcinfo/vmware-automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sddcinfo/vmware-automation/discussions)  
- **Documentation**: [Wiki](https://github.com/sddcinfo/vmware-automation/wiki)

---
**⭐ Star this repository if you find it helpful!**
