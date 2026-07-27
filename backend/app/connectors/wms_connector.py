"""Warehouse Management System connector."""

from typing import Any, Dict, Iterable

from app.connectors.universal_connector import UniversalRESTConnector


class WMSConnector(UniversalRESTConnector):
    connector_type = "wms"

    def inventory_positions(self):
        self.config["url"] = self.config.get("inventory_url") or self.config.get("url")
        return self.extract()

    def shipment_confirmations(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        self.config["target_url"] = self.config.get("shipment_confirmation_url") or self.config.get("target_url") or self.config.get("url")
        return self.push(records)
