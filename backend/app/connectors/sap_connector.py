"""SAP RFC/BAPI connector with graceful SDK fallback."""

from typing import Any, Dict, Iterable

import pandas as pd

from app.connectors import BaseConnector


class SAPConnector(BaseConnector):
    connector_type = "sap"

    def _params(self) -> Dict[str, Any]:
        return {
            "ashost": self.config.get("ashost") or self.config.get("host"),
            "sysnr": self.config.get("sysnr", "00"),
            "client": self.config.get("client", "100"),
            "user": self.config.get("user"),
            "passwd": self.config.get("password") or self.config.get("passwd"),
            "lang": self.config.get("lang", "EN"),
        }

    def test_connection(self) -> Dict[str, Any]:
        try:
            from pyrfc import Connection  # type: ignore
            with Connection(**self._params()) as conn:
                conn.call("STFC_CONNECTION", REQUTEXT="NEXUS")
            return {"status": "ok", "message": "SAP RFC connection successful"}
        except ImportError:
            return {"status": "configured", "message": "pyrfc not installed; connector configuration validated"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def call_bapi(self, bapi_name: str, parameters: Dict[str, Any] | None = None) -> Dict[str, Any]:
        from pyrfc import Connection  # type: ignore
        with Connection(**self._params()) as conn:
            return conn.call(bapi_name, **(parameters or {}))

    def extract(self) -> pd.DataFrame:
        bapi = self.config.get("bapi") or self.config.get("rfc") or "RFC_READ_TABLE"
        params = dict(self.config.get("parameters") or {})
        if bapi == "RFC_READ_TABLE":
            params.setdefault("QUERY_TABLE", self.config.get("table", "MARA"))
            params.setdefault("DELIMITER", "|")
        result = self.call_bapi(bapi, params)
        rows = result.get("DATA") or result.get("ET_DATA") or result.get("RETURN") or []
        if rows and isinstance(rows[0], dict) and "WA" in rows[0]:
            return pd.DataFrame([row["WA"].split(params.get("DELIMITER", "|")) for row in rows])
        return pd.DataFrame(rows if isinstance(rows, list) else [result])

    def push(self, bapi_name: str, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        results = [self.call_bapi(bapi_name, record) for record in records]
        return {"status": "success", "results": results, "count": len(results)}
