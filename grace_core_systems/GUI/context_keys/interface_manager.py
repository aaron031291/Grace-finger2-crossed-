import threading
from copy import deepcopy
from pydantic import BaseModel
from typing import Dict, Optional, Literal
from display_config import active_config

class UIState(BaseModel):
    visible_panels: Dict[str, bool]
    theme_mode: Literal["light", "dark"]
    active_layout: str
    overrides: Dict[str, str] = {}

class InterfaceManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.base_config = deepcopy(active_config)
        self.live_state = UIState(
            visible_panels={k: v.default_visible for k, v in active_config.panels.items()},
            theme_mode=active_config.theme.mode,
            active_layout="default"
        )

    def get_current_state(self) -> UIState:
        with self._lock:
            return self.live_state.copy()

    def toggle_panel(self, panel_id: str, visible: Optional[bool] = None):
        with self._lock:
            if panel_id not in self.base_config.panels:
                raise ValueError(f"Invalid panel ID: {panel_id}")
            
            if visible is None:
                self.live_state.visible_panels[panel_id] = not self.live_state.visible_panels.get(panel_id, False)
            else:
                self.live_state.visible_panels[panel_id] = visible
            
            self.live_state.overrides[f"panel_{panel_id}"] = str(self.live_state.visible_panels[panel_id])

    def set_theme(self, mode: Literal["light", "dark"]):
        with self._lock:
            self.live_state.theme_mode = mode
            self.live_state.overrides["theme"] = mode

    def set_layout_preset(self, preset_name: str):
        with self._lock:
            if preset_name not in self.base_config.graph_layouts:
                raise ValueError(f"Invalid layout preset: {preset_name}")
            self.live_state.active_layout = preset_name
            self.live_state.overrides["layout"] = preset_name

    def restore_defaults(self, component: Optional[str] = None):
        with self._lock:
            if component == "theme":
                self.live_state.theme_mode = self.base_config.theme.mode
                del self.live_state.overrides["theme"]
            elif component == "layout":
                self.live_state.active_layout = "default"
                del self.live_state.overrides["layout"]
            elif component and component.startswith("panel_"):
                panel_id = component.split("_", 1)[1]
                self.live_state.visible_panels[panel_id] = self.base_config.panels[panel_id].default_visible
                del self.live_state.overrides[f"panel_{panel_id}"]
            elif component is None:
                self.live_state = UIState(
                    visible_panels={k: v.default_visible for k, v in self.base_config.panels.items()},
                    theme_mode=self.base_config.theme.mode,
                    active_layout="default"
                )
                self.live_state.overrides.clear()

    def generate_client_config(self) -> Dict:
        with self._lock:
            return {
                "theme": self.live_state.theme_mode,
                "layout": self.base_config.get_graph_style(self.live_state.active_layout),
                "panels": self.live_state.visible_panels,
                "overrides": self.live_state.overrides
            }

# Singleton instance
interface_manager = InterfaceManager()