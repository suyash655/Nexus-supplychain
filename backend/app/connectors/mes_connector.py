"""Manufacturing Execution System connector."""

from typing import Any, Dict, Iterable

from app.connectors.universal_connector import UniversalRESTConnector


class MESConnector(UniversalRESTConnector):
    connector_type = "mes"

    def production_orders(self):
        self.config["url"] = self.config.get("production_orders_url") or self.config.get("url")
        return self.extract()

    def equipment_status(self):
        self.config["url"] = self.config.get("equipment_status_url") or self.config.get("url")
        return self.extract()

    def report_completion(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        self.config["target_url"] = self.config.get("completion_url") or self.config.get("target_url") or self.config.get("url")
        return self.push(records)
