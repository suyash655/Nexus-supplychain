"""Transportation Management System connector."""

from typing import Any, Dict, Iterable

from app.connectors.universal_connector import UniversalRESTConnector


class TMSConnector(UniversalRESTConnector):
    connector_type = "tms"

    def carrier_status(self):
        self.config["url"] = self.config.get("carrier_status_url") or self.config.get("url")
        return self.extract()

    def tender_loads(self, loads: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        self.config["target_url"] = self.config.get("tender_url") or self.config.get("target_url") or self.config.get("url")
        return self.push(loads)
