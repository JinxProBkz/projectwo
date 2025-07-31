import re
import json
import os
from collections import defaultdict

# Folder konfigurasi
INPUT_FOLDER = "file ssh"
ARP_FOLDER = "ip arp"
OUTPUT_FOLDER = "output json"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --------------------------
# Parsing bagian interface
# --------------------------

def parse_ios_status(status_section):
    """
    Parser fleksibel untuk 'show int status' di IOS.
    Ambil kolom dari belakang agar lebih stabil walau deskripsi kosong atau spasi tidak rata.
    """
    port_data = {}
    for line in status_section.splitlines():
        if not line.strip() or line.startswith("Port") or line.startswith("---"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue  # skip benar-benar rusak
        try:
            # Ambil dari belakang
            type_ = parts[-1]
            speed = parts[-2]
            duplex = parts[-3]
            vlan = parts[-4]
            status = parts[-5]
            port = parts[0]
            name = " ".join(parts[1:-5])
            port_data[port] = {
                'description': name.strip(),
                'status': status.strip(),
                'vlan': vlan.strip(),
                'duplex': duplex.strip(),
                'speed': speed.strip(),
                'type': type_.strip(),
                'mac_addresses': [],
                'ip_addresses': []
            }
        except Exception as e:
            print(f"[!] Failed parsing line: {line}")
            continue
    return port_data


def parse_ios_status_fallback(status_section):
    """
    Fallback parser jika parsing utama gagal: lebih toleran terhadap spasi tidak rata.
    Cocok jika kolom 'Name' kosong, atau spacing tidak konsisten.
    """
    port_data = {}
    for line in status_section.splitlines():
        if not line.strip() or line.startswith("Port") or line.startswith("---"):
            continue
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            port = parts[0]
            type_ = parts[-1]
            speed = parts[-2]
            duplex = parts[-3]
            vlan = parts[-4]
            status = parts[-5]
            name = " ".join(parts[1:-5])
            port_data[port] = {
                'description': name.strip(),
                'status': status.strip(),
                'vlan': vlan.strip(),
                'duplex': duplex.strip(),
                'speed': speed.strip(),
                'type': type_.strip(),
                'mac_addresses': [],
                'ip_addresses': []
            }
        except IndexError:
            continue
    return port_data


def parse_ios_desc(desc_section):
    """Parse bagian 'show int desc' untuk Cisco IOS."""
    desc_map = {}
    for line in desc_section.splitlines():
        if not line.strip() or line.startswith("Interface") or line.startswith("---"):
            continue
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 4:
            iface = parts[0]
            desc = parts[3]
            desc_map[iface] = desc
    return desc_map


def parse_nexus_status(status_section):
    """
    Parse 'show int status' untuk Cisco Nexus.
    Ambil port (kolom 1), 5 kolom terakhir (Status, Vlan, Duplex, Speed, Type),
    dan isi description dengan kosong dulu, karena nanti diisi dari show int desc.
    """
    port_data = {}
    for line in status_section.splitlines():
        if not line.strip() or line.startswith("Port") or line.startswith("---"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        port = parts[0]
        type_ = parts[-1]
        speed = parts[-2]
        duplex = parts[-3]
        vlan = parts[-4]
        status = parts[-5]
        port_data[port] = {
            'description': "",  # Nanti diganti dari show int desc
            'status': status.strip(),
            'vlan': vlan.strip(),
            'duplex': duplex.strip(),
            'speed': speed.strip(),
            'type': type_.strip(),
            'mac_addresses': [],
            'ip_addresses': []
        }
    return port_data




def parse_nexus_desc(desc_section):
    desc_map = {}
    for line in desc_section.splitlines():
        line = line.strip()
        if not line or line.startswith("Interface") or line.startswith("---") or line.startswith("Port"):
            continue
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 2:
            iface = parts[0]
            desc = parts[-1]
            desc_map[iface] = desc
    return desc_map


def parse_mac_table(mac_section):
    """Parse bagian 'show mac address-table'."""
    mac_table = defaultdict(list)
    for line in mac_section.splitlines():
        if not line.strip() or "MAC" in line or "----" in line or "Legend" in line:
            continue
        match = re.match(r'^\*?\s*(\d+)\s+([0-9a-fA-F\.]+)\s+\S+\s+.*?(\S+)$', line.strip())
        if match:
            vlan = match.group(1)
            mac = match.group(2).lower()
            port = match.group(3)
            mac_table[port].append({'mac': mac, 'vlan': vlan})
    return mac_table


def merge_description(port_data, desc_map):
    for iface, desc in desc_map.items():
        if iface in port_data and desc:
            port_data[iface]['description'] = desc
    return port_data


def extract_section_single(content, command):
    """
    Versi original: Ambil satu blok show command saja (pertama kali ditemukan).
    """
    pattern = rf'^\s*(?:---\s*)?({command}|{command.replace("int", "interface")})\s*$'
    lines = content.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if re.search(pattern, line.strip(), re.IGNORECASE):
            start_idx = i + 1
            break
    if start_idx is None:
        return ""

    section_lines = []
    for line in lines[start_idx:]:
        if re.search(r'^\s*(---\s*show|show\s+\S+)', line, re.IGNORECASE):
            break
        section_lines.append(line)
    return "\n".join(section_lines).strip()


def extract_section_multi(content, command):
    """
    Versi fallback: Ambil semua blok show command (jika muncul lebih dari sekali).
    Memperbaiki kasus dengan spasi setelah '#' seperti:
    'ID-PLZSF-ACsW-GMP-2903# show int status '
    """
    # Perbolehkan spasi di antara '#' dan 'show'
    pattern = re.compile(rf'^\s*ID-\S+#\s*({command}|{command.replace("int", "interface")})\s*$', re.IGNORECASE)
    lines = content.splitlines()
    sections = []
    current_section = []
    capture = False

    for line in lines:
        if pattern.match(line):
            if capture and current_section:
                sections.append("\n".join(current_section).strip())
                current_section = []
            capture = True
            continue
        elif re.match(r'^\s*ID-\S+#\s*show\s+\S+', line.strip(), re.IGNORECASE):
            if capture and current_section:
                sections.append("\n".join(current_section).strip())
                current_section = []
                capture = False
            continue

        if capture:
            current_section.append(line)

    if capture and current_section:
        sections.append("\n".join(current_section).strip())

    return "\n".join(sections)


def extract_section_from_prompt(content, command):
    """
    Ekstrak blok 'show int status', 'show int desc', atau 'show mac address-table'
    dari file yang mengandung baris 'hostname#command'.
    """
    pattern = re.compile(rf'^\s*\S+#\s*{re.escape(command)}\s*$', re.IGNORECASE)
    lines = content.splitlines()
    sections = []
    current_section = []
    capture = False

    for line in lines:
        if pattern.match(line.strip()):
            capture = True
            current_section = []
            continue
        elif re.match(r'^\s*\S+#\s*show\s+\S+', line.strip(), re.IGNORECASE):
            if capture:
                break
        if capture:
            current_section.append(line)

    return "\n".join(current_section).strip()

PARSERS = {
    "ios": {
        "status": lambda section: parse_ios_status(section) or parse_ios_status_fallback(section),
        "desc": parse_ios_desc
    },
    "nexus": {
        "status": lambda section: parse_nexus_status(section),
        "desc": parse_nexus_desc
    }
}


def parse_switch_data(file_content):
    # Ekstrak blok
    status_block = extract_section_single(file_content, "show int status")
    if not status_block or len(status_block.splitlines()) < 3:
        status_block = extract_section_multi(file_content, "show int status")
    if not status_block or len(status_block.splitlines()) < 3:
        status_block = extract_section_from_prompt(file_content, "show int status")

    desc_block = extract_section_single(file_content, "show int desc")
    if not desc_block or len(desc_block.splitlines()) < 3:
        desc_block = extract_section_multi(file_content, "show int desc")
    if not desc_block or len(desc_block.splitlines()) < 3:
        desc_block = extract_section_from_prompt(file_content, "show int desc")

    mac_block = extract_section_single(file_content, "show mac address-table")
    if not mac_block or len(mac_block.splitlines()) < 3:
        mac_block = extract_section_multi(file_content, "show mac address-table")
    if not mac_block or len(mac_block.splitlines()) < 3:
        mac_block = extract_section_from_prompt(file_content, "show mac address-table")

    if not status_block:
        return {}

    # Deteksi IOS atau Nexus
    is_ios = "Gi" in status_block or "Fa" in status_block
    parsers = PARSERS["ios"] if is_ios else PARSERS["nexus"]

    # Modular parsing
    port_data = parsers["status"](status_block)
    if not port_data or len(port_data) < 3:
        print("[!] Warning: Port parsing hasilnya kecil. Coba perbaiki regex/format.")
    desc_map = parsers["desc"](desc_block)
    port_data = merge_description(port_data, desc_map)

    # MAC parsing
    mac_table = parse_mac_table(mac_block)
    for port, macs in mac_table.items():
        normalized_port = port.replace("Ethernet", "Eth").replace("Port-channel", "Po")
        if port in port_data:
            port_data[port]['mac_addresses'] = macs
        elif normalized_port in port_data:
            port_data[normalized_port]['mac_addresses'] = macs
    print(f"[+] Parsed {len(port_data)} ports from 'show int status'")

    return port_data






# --------------------------
# Parsing ARP (IP Address)
# --------------------------

def parse_arp_data(arp_section):
    arp_data = {}
    for line in arp_section.splitlines():
        match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})\s+\S+\s+([0-9a-f.]{4}\.[0-9a-f.]{4}\.[0-9a-f.]{4})", line, re.IGNORECASE)
        if match:
            ip = match.group(1)
            mac = match.group(2).lower()
            if mac not in arp_data:
                arp_data[mac] = []
            arp_data[mac].append(ip)
    print(f"[i] Total ARP entries parsed: {len(arp_data)}")
    for m, ips in list(arp_data.items())[:3]:
        print(f"    {m}: {ips}")

    return arp_data





def load_all_arp_data():
    arp_data = {}
    if not os.path.exists(ARP_FOLDER):
        return arp_data
    arp_files = [f for f in os.listdir(ARP_FOLDER) if f.lower().endswith(".txt")]
    for arp_file in arp_files:
        with open(os.path.join(ARP_FOLDER, arp_file), 'r', encoding='utf-8') as f:
            content = f.read()
        parsed = parse_arp_data(content)
        for mac, ips in parsed.items():
            if mac not in arp_data:
                arp_data[mac] = []
            arp_data[mac].extend(ips)
    return arp_data


# --------------------------
# Main Processing
# --------------------------

def process_all_files():
    arp_data = load_all_arp_data()
    switch_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.txt')]
    for switch_file in switch_files:
        with open(os.path.join(INPUT_FOLDER, switch_file), 'r', encoding='utf-8-sig') as f:
              content = f.read()
        port_data = parse_switch_data(content)

        # Tambahkan IP address
        for port, pdata in port_data.items():
            ips = []
            for mac_entry in pdata.get('mac_addresses', []):
                mac = mac_entry['mac']
                if mac in arp_data:
                    ips.extend(arp_data[mac])
            pdata['ip_addresses'] = list(set(ips))

        output_path = os.path.join(OUTPUT_FOLDER, switch_file.replace('.txt', '.json'))
        with open(output_path, 'w', encoding='utf-8') as out:
            json.dump(port_data, out, indent=2)
        print(f"Created {output_path}")


if __name__ == "__main__":
    print(f"Starting conversion of all switch files in {INPUT_FOLDER}...")
    process_all_files()
    print("\nConversion completed!")


