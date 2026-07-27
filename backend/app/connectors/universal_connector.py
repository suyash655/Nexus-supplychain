"""
Universal REST/SOAP connector adapters.

These adapters intentionally use the Python standard library so the connector
layer remains deployable without optional enterprise SDKs.
"""

import base64
import json
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, Optional
from xml.etree import ElementTree

import pandas as pd

from app.connectors import BaseConnector


class UniversalRESTConnector(BaseConnector):
    connector_type = "universal_rest"

    def _headers(self) -> Dict[str, str]:
        headers = dict(self.config.get("headers") or {})
        auth = self.config.get("auth") or {}
        if auth.get("type") == "bearer" and auth.get("token"):
            headers["Authorization"] = f"Bearer {auth['token']}"
        elif auth.get("type") == "basic":
            raw = f"{auth.get('username', '')}:{auth.get('password', '')}"
            headers["Authorization"] = "Basic " + base64.b64encode(raw.encode()).decode()
        return headers

    def _request(self, method: str, url: str, body: Optional[bytes] = None) -> Any:
        req = urllib.request.Request(url, data=body, method=method.upper())
        for key, value in self._headers().items():
            req.add_header(key, value)
        with urllib.request.urlopen(req, timeout=int(self.config.get("timeout", 30))) as resp:
            payload = resp.read().decode()
            content_type = resp.headers.get("Content-Type", "")
            if "json" in content_type or payload[:1] in ("{", "["):
                return json.loads(payload)
            return payload

    def test_connection(self) -> Dict[str, Any]:
        try:
            url = self.config.get("health_url") or self.config.get("url")
            if not url:
                return {"status": "error", "message": "Missing url"}
            self._request(self.config.get("health_method", "GET"), url)
            return {"status": "ok", "message": "REST endpoint reachable"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def extract(self) -> pd.DataFrame:
        data = self._request(self.config.get("method", "GET"), self.config["url"])
        data_path = self.config.get("data_path")
        if data_path:
            for key in data_path.split("."):
                if isinstance(data, dict):
                    data = data.get(key, [])
                elif isinstance(data, list) and key.isdigit():
                    data = data[int(key)]
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            return pd.DataFrame([data])
        return pd.DataFrame([{"payload": data}])

    def push(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        target_url = self.config.get("target_url") or self.config.get("url")
        body = json.dumps(list(records)).encode()
        data = self._request(self.config.get("push_method", "POST"), target_url, body)
        return {"status": "success", "response": data}


class UniversalSOAPConnector(BaseConnector):
    connector_type = "universal_soap"

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        headers.update(self.config.get("headers") or {})
        if self.config.get("soap_action"):
            headers["SOAPAction"] = self.config["soap_action"]
        return headers

    def _envelope(self) -> str:
        body = self.config.get("body", "")
        if "<soap" in body.lower():
            return body
        return (
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
            "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">"
            f"<soap:Body>{body}</soap:Body></soap:Envelope>"
        )

    def test_connection(self) -> Dict[str, Any]:
        try:
            url = self.config.get("wsdl_url") or self.config.get("url")
            if not url:
                return {"status": "error", "message": "Missing url"}
            with urllib.request.urlopen(url, timeout=int(self.config.get("timeout", 30))) as resp:
                return {"status": "ok", "message": f"SOAP endpoint reachable ({resp.status})"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def extract(self) -> pd.DataFrame:
        req = urllib.request.Request(self.config["url"], data=self._envelope().encode(), method="POST")
        for key, value in self._headers().items():
            req.add_header(key, value)
        try:
            with urllib.request.urlopen(req, timeout=int(self.config.get("timeout", 30))) as resp:
                xml_text = resp.read().decode()
        except urllib.error.HTTPError as exc:
            xml_text = exc.read().decode()
            raise RuntimeError(f"SOAP request failed: {exc.code} {xml_text[:300]}") from exc

        rows = []
        root = ElementTree.fromstring(xml_text)
        for element in root.iter():
            children = list(element)
            if children and all(len(list(child)) == 0 for child in children):
                rows.append({child.tag.split("}")[-1]: child.text for child in children})
        return pd.DataFrame(rows or [{"response": xml_text}])


UniversalConnector = UniversalRESTConnector
