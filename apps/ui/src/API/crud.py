try:
    import requests  # preferred
except ModuleNotFoundError:  # mobile fallback: use httpx shim
    import httpx

    class _RequestsShim:
        class exceptions:
            RequestException = httpx.HTTPError

        class Session:
            def __init__(self):
                self._client = httpx.Client()
                self.headers = {}

            def request(
                self,
                *,
                method: str,
                url: str,
                params=None,
                headers=None,
                json=None,
                data=None,
                timeout=None,
            ):
                merged_headers = {**self.headers, **(headers or {})}
                return self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=merged_headers,
                    json=json,
                    data=data,
                    timeout=timeout,
                )

    requests = _RequestsShim()  # type: ignore
from typing import Any, Dict, Optional, Tuple, Union

JSON = Union[Dict[str, Any], list, None]


class RestClient:
    """
    Cliente REST genérico para CRUD.
    Uso:
        api = RestClient(base_url="https://69069a11b1879c890ed7a77d.mockapi.io/")
        ok, data, status = api.get("users")                      # LIST
        ok, data, status = api.get("users/1")                   # GET by id
        ok, data, status = api.post("users", json={...})        # CREATE
        ok, data, status = api.patch("users/1", json={...})     # PARTIAL UPDATE
        ok, data, status = api.put("users/1", json={...})       # REPLACE
        ok, _,   status = api.delete("users/1")                 # DELETE
    """

    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: int = 12,
        raise_on_http_error: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.raise_on_http_error = raise_on_http_error
        self._session = requests.Session()
        self._session.headers.update(self.default_headers)

    # -------- core request ----------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json: JSON = None,
        data: Any = None,
    ) -> Tuple[bool, JSON, int, Optional[str]]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        merged_headers = {**self.default_headers, **(headers or {})}

        try:
            resp = self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                headers=merged_headers,
                json=json,
                data=data,
                timeout=self.timeout,
            )

            if self.raise_on_http_error:
                resp.raise_for_status()

            status = resp.status_code

            # intenta decodificar JSON, si no, regresa texto
            try:
                payload: JSON = resp.json() if resp.content else None
            except ValueError:
                payload = {"raw": resp.text} if resp.text else None

            ok = 200 <= status < 300
            err = None if ok else f"HTTP {status}"
            return ok, payload, status, err

        except requests.exceptions.RequestException as e:
            return False, None, 0, str(e)

    # -------- public helpers ----------
    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        return self._request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        *,
        json: JSON = None,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        return self._request("POST", path, params=params, headers=headers, json=json, data=data)

    def put(
        self,
        path: str,
        *,
        json: JSON = None,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        return self._request("PUT", path, params=params, headers=headers, json=json, data=data)

    def patch(
        self,
        path: str,
        *,
        json: JSON = None,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        return self._request("PATCH", path, params=params, headers=headers, json=json, data=data)

    def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        return self._request("DELETE", path, params=params, headers=headers)
