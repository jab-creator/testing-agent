from __future__ import annotations
from adapters.static_web_adapter import StaticWebAdapter

class AdapterFactory:
    @staticmethod
    def get_adapter(project_type: str):
        project_type = (project_type or "").strip().lower()
        if project_type == "static_web":
            return StaticWebAdapter()
        raise ValueError(f"Unsupported project.type: {project_type}")
