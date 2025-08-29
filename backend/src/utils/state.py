from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
import threading

@dataclass
class DataStore:
    # raw dataframes dumped to records
    hyperv: List[dict] = field(default_factory=list)
    exchange: List[dict] = field(default_factory=list)
    s3: List[dict] = field(default_factory=list)

    # mapping: key -> {company_name, bin}
    map_hyperv: Dict[str, dict] = field(default_factory=dict)
    map_exchange: Dict[str, dict] = field(default_factory=dict)
    map_s3: Dict[str, dict] = field(default_factory=dict)

    # cached computed reports
    report_hyperv: List[dict] = field(default_factory=list)
    report_exchange: List[dict] = field(default_factory=list)
    report_s3: List[dict] = field(default_factory=list)
    report_summary: List[dict] = field(default_factory=list)

class AppState:
    _lock = threading.Lock()
    _data = DataStore()

    @classmethod
    def get(cls) -> DataStore:
        return cls._data

    @classmethod
    def update(cls, **kwargs):
        with cls._lock:
            for k, v in kwargs.items():
                setattr(cls._data, k, v)

    @classmethod
    def clear_reports(cls):
        with cls._lock:
            cls._data.report_hyperv.clear()
            cls._data.report_exchange.clear()
            cls._data.report_s3.clear()
            cls._data.report_summary.clear()
