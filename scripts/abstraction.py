import pandas as pd

RAW_PATH = "data/raw_timeline.csv"
OUTPUT_PATH = "data/abstracted_timeline.csv"

# Forensic timeline abstraction rules
rules = {
    # File System Activities
    "file_create": "File System Activity",
    "file_delete": "File System Activity", 
    "file_modify": "File System Activity",
    "file_execute": "File System Activity",
    "file_encrypt": "File System Activity",
    "file_entry": "File System Activity",
    
    # Registry Activities
    "key_add": "Registry Change",
    "key_create": "Registry Change",
    "key_modify": "Registry Change",
    "key_delete": "Registry Change",
    "key_access": "Registry Change",
    "reg_add": "Registry Change",
    
    # Network Activities
    "connection_outbound": "Network Activity",
    "connection_inbound": "Network Activity",
    "data_exfiltration": "Network Activity",
    "download_event": "Network Activity",
    
    # User & System Events
    "user_logon": "User Activity",
    "user_logoff": "User Activity",
    "boot_event": "System Event",
    "system_shutdown": "System Event",
    "logon_event": "User Activity",
    
    # Process Activities
    "process_create": "Process Activity",
    "process_terminate": "Process Activity",
    
    # Browser Activities
    "browser_cache": "Web Browsing",
    "cache_write": "Web Browsing"
}

def abstract_events():
    df = pd.read_csv(RAW_PATH)
    df["abstracted_action"] = df["action"].map(rules).fillna("Other Activity")

    # Example: drop duplicate consecutive events
    df = df.drop_duplicates(subset=["timestamp", "abstracted_action"])
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[+] Abstracted timeline saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    abstract_events()
