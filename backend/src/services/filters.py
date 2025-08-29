import re

# Hyper-V: exclude VMOwner contains these (case-insensitive)
EXCLUDE_VMOWNERS = [r"id\.kz", r"cloud24\.kz", r"test", r"demo"]

# Exchange: exact names to exclude
EXCLUDE_CUSTOMERS = {
    "Service Provider", "test customer", "Belltower Group", "Demo Company 1", "FTP TEST"
}

# S3: exclude owners (column B) if contains these (case-insensitive)
EXCLUDE_S3_OWNERS = [
    r"admin@demo1\.kz", r"admin@demo2\.kz", r"dbaioralov@id\.kz",
    r"nextcloud-prod", r"nextcloud\.demo1", r"nextcloud\.demo2",
    r"nextcloud\.test1", r"nextcloud\.testnew", r"s-veeam@id\.kz", r"test"
]

def any_regex_match(value: str, patterns):
    if value is None:
        return False
    for p in patterns:
        if re.search(p, value, flags=re.IGNORECASE):
            return True
    return False
