#!/usr/bin/env python3
# ============================================================
# VisionX OS — Lazy Installer
# Automatically installs missing tools when needed
# /usr/local/lib/visionx/python/lazy_install.py
# ============================================================

import subprocess
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

R = Fore.RED + Style.BRIGHT
G = Fore.GREEN + Style.BRIGHT
Y = Fore.YELLOW + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
NC = Style.RESET_ALL

def info(msg):    print(f"  {C}[~]{NC} {msg}")
def ok(msg):      print(f"  {G}[✔]{NC} {msg}")
def warn(msg):    print(f"  {Y}[!]{NC} {msg}")
def error(msg):   print(f"  {R}[✘]{NC} {msg}")

# ── Tool install map ──────────────────────────────────────────
# Format: 'tool_name': ('method', 'package/source')
TOOL_MAP = {
    # APT tools
    'nmap':          ('apt', 'nmap'),
    'netcat':        ('apt', 'netcat-openbsd'),
    'nc':            ('apt', 'netcat-openbsd'),
    'tcpdump':       ('apt', 'tcpdump'),
    'wireshark':     ('apt', 'wireshark'),
    'tshark':        ('apt', 'tshark'),
    'nikto':         ('apt', 'nikto'),
    'sqlmap':        ('apt', 'sqlmap'),
    'gobuster':      ('apt', 'gobuster'),
    'wpscan':        ('gem', 'wpscan'),
    'dirb':          ('apt', 'dirb'),
    'hydra':         ('apt', 'hydra'),
    'medusa':        ('apt', 'medusa'),
    'hashcat':       ('apt', 'hashcat'),
    'john':          ('apt', 'john'),
    'cewl':          ('apt', 'cewl'),
    'crunch':        ('apt', 'crunch'),
    'aircrack-ng':   ('apt', 'aircrack-ng'),
    'reaver':        ('apt', 'reaver'),
    'wifite':        ('apt', 'wifite'),
    'wash':          ('apt', 'reaver'),
    'gdb':           ('apt', 'gdb'),
    'strace':        ('apt', 'strace'),
    'ltrace':        ('apt', 'ltrace'),
    'binwalk':       ('apt', 'binwalk'),
    'strings':       ('apt', 'binutils'),
    'objdump':       ('apt', 'binutils'),
    'exiftool':      ('apt', 'libimage-exiftool-perl'),
    'whois':         ('apt', 'whois'),
    'recon-ng':      ('apt', 'recon-ng'),
    'ufw':           ('apt', 'ufw'),
    'fail2ban':      ('apt', 'fail2ban'),
    'rkhunter':      ('apt', 'rkhunter'),
    'lynis':         ('apt', 'lynis'),
    'htop':          ('apt', 'htop'),
    'vim':           ('apt', 'vim'),
    'tmux':          ('apt', 'tmux'),
    'curl':          ('apt', 'curl'),
    'wget':          ('apt', 'wget'),
    'git':           ('apt', 'git'),
    'gcc':           ('apt', 'gcc'),
    'make':          ('apt', 'make'),
    'docker':        ('apt', 'docker.io'),
    'hcxtools':      ('apt', 'hcxtools'),
    # Go tools
    'ffuf':          ('go', 'github.com/ffuf/ffuf/v2@latest'),
    'nuclei':        ('go', 'github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest'),
    # Python/venv tools
    'theHarvester':  ('venv', '/opt/theharvester-env'),
    'sherlock':      ('venv', '/opt/sherlock-env'),
    'wafw00f':       ('venv', '/opt/wafw00f-env'),
    # Git tools
    'radare2':       ('git', 'https://github.com/radareorg/radare2'),
}

def is_installed(tool):
    """Check if a tool is already installed."""
    # Check PATH
    result = subprocess.run(f"command -v {tool}", shell=True,
                           capture_output=True, text=True)
    if result.returncode == 0:
        return True
    # Check dpkg
    result = subprocess.run(f"dpkg -l {tool} 2>/dev/null | grep -q '^ii'",
                           shell=True, capture_output=True)
    if result.returncode == 0:
        return True
    # Check venv
    venv_path = f"/opt/{tool.lower()}-env/bin/{tool}"
    if os.path.exists(venv_path):
        return True
    return False

def install_apt(package):
    """Install via apt."""
    info(f"Installing {package} via apt...")
    result = subprocess.run(
        f"sudo apt-get install -y -qq {package}",
        shell=True, capture_output=True, text=True
    )
    return result.returncode == 0

def install_gem(package):
    """Install via gem."""
    info(f"Installing {package} via gem...")
    result = subprocess.run(
        f"sudo gem install {package}",
        shell=True, capture_output=True, text=True
    )
    return result.returncode == 0

def install_go(package):
    """Install via go."""
    info(f"Installing {package} via go...")
    env = os.environ.copy()
    env['GOPATH'] = '/opt/visionx/go'
    result = subprocess.run(
        f"go install {package}",
        shell=True, capture_output=True, text=True, env=env
    )
    tool_name = package.split('/')[-1].split('@')[0]
    subprocess.run(
        f"sudo ln -sf /opt/visionx/go/bin/{tool_name} /usr/local/bin/{tool_name}",
        shell=True
    )
    return result.returncode == 0

def install_tool(tool):
    """Main install function — detects method and installs."""
    if tool not in TOOL_MAP:
        warn(f"No install recipe for '{tool}' — install manually")
        return False

    if is_installed(tool):
        ok(f"{tool} is already installed")
        return True

    method, source = TOOL_MAP[tool]

    if method == 'apt':
        success = install_apt(source)
    elif method == 'gem':
        success = install_gem(source)
    elif method == 'go':
        success = install_go(source)
    elif method == 'venv':
        warn(f"{tool} requires manual venv setup")
        print(f"  {C}Run: visionx install osint{NC}")
        return False
    else:
        warn(f"Unknown install method for {tool}")
        return False

    if success:
        ok(f"{tool} installed successfully")
    else:
        error(f"Failed to install {tool}")

    return success

def ensure_tool(tool):
    """
    Called by other scripts to ensure a tool exists.
    Installs it automatically if missing.
    Returns True if tool is available.
    """
    if is_installed(tool):
        return True

    warn(f"Tool '{tool}' not found — attempting auto-install...")
    return install_tool(tool)

def check_and_install_list(tools):
    """Check and install a list of tools."""
    missing = [t for t in tools if not is_installed(t)]

    if not missing:
        ok("All required tools are installed")
        return True

    warn(f"Missing tools: {', '.join(missing)}")
    print()

    for tool in missing:
        install_tool(tool)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"\n  {C}Usage:{NC}")
        print(f"  python3 lazy_install.py <tool>        — install single tool")
        print(f"  python3 lazy_install.py check <tool>  — check if installed\n")
        sys.exit(1)

    if sys.argv[1] == 'check':
        tool = sys.argv[2] if len(sys.argv) > 2 else ''
        if is_installed(tool):
            ok(f"{tool} is installed")
        else:
            error(f"{tool} is not installed")
    else:
        install_tool(sys.argv[1])#!/usr/bin/env python3
# ============================================================
# VisionX OS — Lazy Installer
# Automatically installs missing tools when needed
# /usr/local/lib/visionx/python/lazy_install.py
# ============================================================

import subprocess
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

R = Fore.RED + Style.BRIGHT
G = Fore.GREEN + Style.BRIGHT
Y = Fore.YELLOW + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
NC = Style.RESET_ALL

def info(msg):    print(f"  {C}[~]{NC} {msg}")
def ok(msg):      print(f"  {G}[✔]{NC} {msg}")
def warn(msg):    print(f"  {Y}[!]{NC} {msg}")
def error(msg):   print(f"  {R}[✘]{NC} {msg}")

# ── Tool install map ──────────────────────────────────────────
# Format: 'tool_name': ('method', 'package/source')
TOOL_MAP = {
    # APT tools
    'nmap':          ('apt', 'nmap'),
    'netcat':        ('apt', 'netcat-openbsd'),
    'nc':            ('apt', 'netcat-openbsd'),
    'tcpdump':       ('apt', 'tcpdump'),
    'wireshark':     ('apt', 'wireshark'),
    'tshark':        ('apt', 'tshark'),
    'nikto':         ('apt', 'nikto'),
    'sqlmap':        ('apt', 'sqlmap'),
    'gobuster':      ('apt', 'gobuster'),
    'wpscan':        ('gem', 'wpscan'),
    'dirb':          ('apt', 'dirb'),
    'hydra':         ('apt', 'hydra'),
    'medusa':        ('apt', 'medusa'),
    'hashcat':       ('apt', 'hashcat'),
    'john':          ('apt', 'john'),
    'cewl':          ('apt', 'cewl'),
    'crunch':        ('apt', 'crunch'),
    'aircrack-ng':   ('apt', 'aircrack-ng'),
    'reaver':        ('apt', 'reaver'),
    'wifite':        ('apt', 'wifite'),
    'wash':          ('apt', 'reaver'),
    'gdb':           ('apt', 'gdb'),
    'strace':        ('apt', 'strace'),
    'ltrace':        ('apt', 'ltrace'),
    'binwalk':       ('apt', 'binwalk'),
    'strings':       ('apt', 'binutils'),
    'objdump':       ('apt', 'binutils'),
    'exiftool':      ('apt', 'libimage-exiftool-perl'),
    'whois':         ('apt', 'whois'),
    'recon-ng':      ('apt', 'recon-ng'),
    'ufw':           ('apt', 'ufw'),
    'fail2ban':      ('apt', 'fail2ban'),
    'rkhunter':      ('apt', 'rkhunter'),
    'lynis':         ('apt', 'lynis'),
    'htop':          ('apt', 'htop'),
    'vim':           ('apt', 'vim'),
    'tmux':          ('apt', 'tmux'),
    'curl':          ('apt', 'curl'),
    'wget':          ('apt', 'wget'),
    'git':           ('apt', 'git'),
    'gcc':           ('apt', 'gcc'),
    'make':          ('apt', 'make'),
    'docker':        ('apt', 'docker.io'),
    'hcxtools':      ('apt', 'hcxtools'),
    # Go tools
    'ffuf':          ('go', 'github.com/ffuf/ffuf/v2@latest'),
    'nuclei':        ('go', 'github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest'),
    # Python/venv tools
    'theHarvester':  ('venv', '/opt/theharvester-env'),
    'sherlock':      ('venv', '/opt/sherlock-env'),
    'wafw00f':       ('venv', '/opt/wafw00f-env'),
    # Git tools
    'radare2':       ('git', 'https://github.com/radareorg/radare2'),
}

def is_installed(tool):
    """Check if a tool is already installed."""
    # Check PATH
    result = subprocess.run(f"command -v {tool}", shell=True,
                           capture_output=True, text=True)
    if result.returncode == 0:
        return True
    # Check dpkg
    result = subprocess.run(f"dpkg -l {tool} 2>/dev/null | grep -q '^ii'",
                           shell=True, capture_output=True)
    if result.returncode == 0:
        return True
    # Check venv
    venv_path = f"/opt/{tool.lower()}-env/bin/{tool}"
    if os.path.exists(venv_path):
        return True
    return False

def install_apt(package):
    """Install via apt."""
    info(f"Installing {package} via apt...")
    result = subprocess.run(
        f"sudo apt-get install -y -qq {package}",
        shell=True, capture_output=True, text=True
    )
    return result.returncode == 0

def install_gem(package):
    """Install via gem."""
    info(f"Installing {package} via gem...")
    result = subprocess.run(
        f"sudo gem install {package}",
        shell=True, capture_output=True, text=True
    )
    return result.returncode == 0

def install_go(package):
    """Install via go."""
    info(f"Installing {package} via go...")
    env = os.environ.copy()
    env['GOPATH'] = '/opt/visionx/go'
    result = subprocess.run(
        f"go install {package}",
        shell=True, capture_output=True, text=True, env=env
    )
    tool_name = package.split('/')[-1].split('@')[0]
    subprocess.run(
        f"sudo ln -sf /opt/visionx/go/bin/{tool_name} /usr/local/bin/{tool_name}",
        shell=True
    )
    return result.returncode == 0

def install_tool(tool):
    """Main install function — detects method and installs."""
    if tool not in TOOL_MAP:
        warn(f"No install recipe for '{tool}' — install manually")
        return False

    if is_installed(tool):
        ok(f"{tool} is already installed")
        return True

    method, source = TOOL_MAP[tool]

    if method == 'apt':
        success = install_apt(source)
    elif method == 'gem':
        success = install_gem(source)
    elif method == 'go':
        success = install_go(source)
    elif method == 'venv':
        warn(f"{tool} requires manual venv setup")
        print(f"  {C}Run: visionx install osint{NC}")
        return False
    else:
        warn(f"Unknown install method for {tool}")
        return False

    if success:
        ok(f"{tool} installed successfully")
    else:
        error(f"Failed to install {tool}")

    return success

def ensure_tool(tool):
    """
    Called by other scripts to ensure a tool exists.
    Installs it automatically if missing.
    Returns True if tool is available.
    """
    if is_installed(tool):
        return True

    warn(f"Tool '{tool}' not found — attempting auto-install...")
    return install_tool(tool)

def check_and_install_list(tools):
    """Check and install a list of tools."""
    missing = [t for t in tools if not is_installed(t)]

    if not missing:
        ok("All required tools are installed")
        return True

    warn(f"Missing tools: {', '.join(missing)}")
    print()

    for tool in missing:
        install_tool(tool)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"\n  {C}Usage:{NC}")
        print(f"  python3 lazy_install.py <tool>        — install single tool")
        print(f"  python3 lazy_install.py check <tool>  — check if installed\n")
        sys.exit(1)

    if sys.argv[1] == 'check':
        tool = sys.argv[2] if len(sys.argv) > 2 else ''
        if is_installed(tool):
            ok(f"{tool} is installed")
        else:
            error(f"{tool} is not installed")
    else:
        install_tool(sys.argv[1])
