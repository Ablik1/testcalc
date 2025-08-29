import os
import sys
import pytest

# Ensure src package is importable when running tests directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from services.naming import get_hyperv_service_name


def test_get_hyperv_service_name_handles_invalid_iops():
    # Invalid or missing IOPS should default to SAS (500 IOPS)
    expected_sas = "Аренда Дискового пространства SAS, 1Гб (500 IOPS)"
    assert get_hyperv_service_name("disk", None) == expected_sas
    assert get_hyperv_service_name("disk", "unknown") == expected_sas

    # Explicit 5000 IOPS should map to the SSD service
    expected_ssd = "Аренда Дискового пространства SSD, 1Гб (5000 IOPS)"
    assert get_hyperv_service_name("disk", 5000) == expected_ssd
