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