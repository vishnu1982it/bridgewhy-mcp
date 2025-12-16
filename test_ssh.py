from netmiko import ConnectHandler

ROUTER = {
    "device_type": "cisco_ios",   # for vIOS 15.6
    "host": "192.168.0.201",      # <-- put your router IP here
    "username": "cisco",          # <-- your SSH username
    "password": "cisco123",       # <-- your SSH password
}

def main():
    conn = ConnectHandler(**ROUTER)
    print("✅ Connected to router")
    output = conn.send_command("show ip interface brief")
    print("\n--- show ip interface brief ---")
    print(output)
    conn.disconnect()
    print("\n✅ Disconnected")

if __name__ == "__main__":
    main()
