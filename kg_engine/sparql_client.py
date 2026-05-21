import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from dotenv import load_dotenv
from SPARQLWrapper import JSON, SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException

load_dotenv()

logger = structlog.get_logger(__name__)

PREFIXES = """
PREFIX cve:   <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cwe:   <http://w3id.org/sepses/vocab/ref/cwe#>
PREFIX capec: <http://w3id.org/sepses/vocab/ref/capec#>
PREFIX cpe:   <http://w3id.org/sepses/vocab/ref/cpe#>
PREFIX cvss:  <http://w3id.org/sepses/vocab/ref/cvss#>
PREFIX res:   <http://w3id.org/sepses/resource/>
PREFIX rescve: <http://w3id.org/sepses/resource/cve/>
PREFIX rescwe: <http://w3id.org/sepses/resource/cwe/>
"""

CVE_URI_BASE   = "http://w3id.org/sepses/resource/cve/"
CWE_URI_BASE   = "http://w3id.org/sepses/resource/cwe/"
CAPEC_URI_BASE = "http://w3id.org/sepses/resource/capec/"

_QUERY_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL = 300

class SparqlClient:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        fallback_endpoint: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self._endpoint = endpoint or os.getenv("SPARQL_ENDPOINT", "https://w3id.org/sepses/sparql")
        self._fallback = fallback_endpoint or os.getenv("FUSEKI_ENDPOINT", "http://localhost:3030/sepses/sparql")
        self._timeout = timeout or int(os.getenv("SPARQL_TIMEOUT_SECONDS", "30"))
        self._queries_dir = Path(__file__).parent / "queries"
        logger.info("sparql_client_init", endpoint=self._endpoint, fallback=self._fallback, timeout=self._timeout)

    def execute_query(self, sparql_str: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        cache_key = sparql_str.strip()
        if use_cache and cache_key in _QUERY_CACHE:
            cached = _QUERY_CACHE[cache_key]
            if time.time() - cached["timestamp"] < _CACHE_TTL:
                logger.debug("cache_hit", query_preview=sparql_str[:80])
                return cached["results"]

        result = self._try_endpoint(self._endpoint, sparql_str)
        if result is None:
            logger.warning("public_endpoint_failed_trying_fallback", endpoint=self._endpoint)
            result = self._try_endpoint(self._fallback, sparql_str)

        if result is None:
            raise RuntimeError(
                f"Kedua SPARQL endpoint tidak tersedia.\n"
                f"Publik: {self._endpoint}\n"
                f"Fallback: {self._fallback}\n"
                f"Jalankan Fuseki lokal atau periksa koneksi internet."
            )

        rows = self._flatten_results(result)
        
        if use_cache:
            _QUERY_CACHE[cache_key] = {"timestamp": time.time(), "results": rows}
        
        logger.info("query_executed", rows_returned=len(rows), query_preview=sparql_str[:80])
        return rows

    def _try_endpoint(self, endpoint_url: str, sparql_str: str) -> Optional[Dict]:
        try:
            wrapper = SPARQLWrapper(endpoint_url)
            wrapper.setQuery(sparql_str)
            wrapper.setReturnFormat(JSON)
            wrapper.setTimeout(self._timeout)
            response = wrapper.query().convert()
            logger.debug("endpoint_success", endpoint=endpoint_url)
            return response
        except SPARQLWrapperException as exc:
            logger.warning("sparql_wrapper_error", endpoint=endpoint_url, error=str(exc))
            return None
        except Exception as exc:
            logger.warning("endpoint_unavailable", endpoint=endpoint_url, error=str(exc))
            return None

    @staticmethod
    def _flatten_results(raw: Dict) -> List[Dict[str, Any]]:
        bindings = raw.get("results", {}).get("bindings", [])
        rows = []
        for binding in bindings:
            row = {}
            for var_name, val_obj in binding.items():
                row[var_name] = val_obj.get("value", "")
            rows.append(row)
        return rows