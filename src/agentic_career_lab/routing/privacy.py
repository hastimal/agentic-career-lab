import json

from pydantic import BaseModel


class PrivacyGuardError(Exception):
    pass


def assert_cloud_safe(payload: BaseModel | dict | str) -> None:
    """Ensure no forbidden keys/data enter the cloud reasoning engine."""
    forbidden_keys = {"raw_resume_text", "resume_text", "email", "phone", "address", "full_resume"}

    if isinstance(payload, BaseModel):
        data = payload.model_dump()
    elif isinstance(payload, str):
        try:
            data = json.loads(payload)
        except Exception:
            data = {}
    else:
        data = payload

    def _check(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in forbidden_keys:
                    raise PrivacyGuardError(f"Forbidden key '{k}' found in payload.")
                if "PRIVATE_RESUME_SECRET_12345" in str(v):
                    raise PrivacyGuardError("Private resume secret found in payload.")
                _check(v)
        elif isinstance(obj, list):
            for item in obj:
                _check(item)

    _check(data)
    if "PRIVATE_RESUME_SECRET_12345" in str(payload):
        raise PrivacyGuardError("Private resume secret found in payload.")
