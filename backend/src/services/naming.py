def get_hyperv_service_name(metric: str, iops: int | float | str | None) -> str:
    metric = (metric or "").lower()
    if metric == "disk":
        try:
            iops_val = int(float(iops)) if iops is not None else 0
        except ValueError:
            iops_val = 0
        return "Аренда Дискового пространства SAS, 1Гб (500 IOPS)" if iops_val == 500             else "Аренда Дискового пространства SSD, 1Гб (5000 IOPS)"
    if metric == "cpu":
        return "Аренда виртуального CPU"
    if metric == "memory":
        return "Аренда Оперативной памяти, 1Гб"
    return metric

STANDARD_TARIFFS = {
    "Exchange 2016, Standard-100GB",
    "Exchange 2016, Standard-50GB",
    "Exchange 2016, Maximum",
    "Exchange 2016, Express",
}
BASIC_TARIFFS = {
    "Exchange 2016, Startup",
    "Exchange 2016, Basic-2GB",
}

def get_exchange_service_name(line_description: str) -> str:
    if line_description in STANDARD_TARIFFS:
        return "Аренда Microsoft Exchange Standard (50ГБ почтовый ящик)"
    if line_description in BASIC_TARIFFS:
        return "Аренда Microsoft Exchange Basic (2ГБ почтовый ящик)"
    # fallback: try to classify
    ld = (line_description or "").lower()
    if "standard" in ld or "maximum" in ld or "express" in ld:
        return "Аренда Microsoft Exchange Standard (50ГБ почтовый ящик)"
    return "Аренда Microsoft Exchange Basic (2ГБ почтовый ящик)"

def get_s3_service_name(owner_name: str) -> str:
    if owner_name and "nextcloud" in owner_name.lower():
        return "Облачное хранилище Nextcloud, 1 Гб"
    return "Объектное хранилище S3"
