import httpx
from app.config import settings

class SharePointConnector:
    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self._token: str = None

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.azure_client_id,
                    "client_secret": settings.azure_client_secret,
                    "scope": "https://graph.microsoft.com/.default",
                },
            )
            self._token = resp.json()["access_token"]
        return self._token

    async def list_files(self, site_url: str, library: str) -> list[dict]:
        token = await self._get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/sites/{site_url}/drives",
                headers={"Authorization": f"Bearer {token}"},
            )
            drives = resp.json().get("value", [])
            drive = next((d for d in drives if d["name"] == library), None)
            if not drive:
                return []
            items_resp = await client.get(
                f"{self.base_url}/drives/{drive['id']}/root/children",
                headers={"Authorization": f"Bearer {token}"},
            )
            return items_resp.json().get("value", [])
