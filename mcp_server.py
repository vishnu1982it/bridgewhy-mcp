import yaml
import ipaddress
from typing import Dict, Any, List

from netmiko import ConnectHandler
from fastmcp import FastMCP

# ---- Load inventory ----
def load_devices() -> Dict[str, Any]:
    with open("devices.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["devices"]

DEVICES = load_devices()

def get_device(name: str) -> Dict[str, Any]:
    if name not in DEVICES:
        raise KeyError(f"Unknown device '{name}' in devices.yaml")
    d = DEVICES[name]
    return {
        "device_type": d["device_type"],
        "host": d["host"],
        "username": d["username"],
        "password": d["password"],
    }

def ssh_show(device: Dict[str, Any], command: str) -> str:
    conn = ConnectHandler(**device)
    out = conn.send_command(command)
    conn.disconnect()
    return out

def ssh_config(device: Dict[str, Any], commands: List[str]) -> str:
    conn = ConnectHandler(**device)
    out = conn.send_config_set(commands)
    conn.disconnect()
    return out

# ---- MCP Server (SSE) ----
mcp = FastMCP("BridgeWhy Network MCP")

@mcp.tool
def show_ip_int_brief(device: str) -> str:
    """Run 'show ip interface brief' on a device."""
    dev = get_device(device)
    return ssh_show(dev, "show ip interface brief")

@mcp.tool
def set_interface_ip(
    device: str,
    interface: str,
    ip: str,
    mask: str,
    no_shutdown: bool = True,
    save: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Configure IPv4 address on an interface. Optionally no shut, save, or dry-run."""
    ipaddress.IPv4Address(ip)
    ipaddress.IPv4Address(mask)

    dev = get_device(device)

    commands = [
        f"interface {interface}",
        f"ip address {ip} {mask}",
    ]
    if no_shutdown:
        commands.append("no shutdown")
    commands.append("exit")

    if dry_run:
        return {"dry_run": True, "commands": commands}

    cfg_out = ssh_config(dev, commands)
    save_out = ssh_show(dev, "write memory") if save else ""
    verify = ssh_show(dev, "show ip interface brief")

    return {
        "applied_commands": commands,
        "config_output": cfg_out,
        "save_output": save_out,
        "verification": verify,
    }

if __name__ == "__main__":
    # ChatGPT “New App” currently expects SSE (text/event-stream)
    mcp.run(transport="sse", host="127.0.0.1", port=2091)
