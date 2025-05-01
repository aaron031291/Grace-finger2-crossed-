from pydantic import BaseModel, Field
from typing import Dict, Optional, Literal
from enum import Enum

class ColorPalette(BaseModel):
    primary: str = "#2b6cb0"  # Grace blue
    secondary: str = "#4299e1"
    background: str = "#1a202c"
    text: str = "#cbd5e0"
    error: str = "#e53e3e"
    warning: str = "#dd6b20"
    success: str = "#38a169"

class ThemeSettings(BaseModel):
    mode: Literal["light", "dark"] = "dark"
    colors: ColorPalette = ColorPalette()
    font_family: str = "Inter, system-ui, sans-serif"
    base_font_size: str = "16px"
    spacing_unit: str = "0.5rem"
    transition_timing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    transition_duration: str = "200ms"

class GraphLayoutPreset(BaseModel):
    name: str
    algorithm: str = "cose"  # cose, dagre, grid, etc.
    padding: int = 50
    node_spacing: int = 75
    edge_length: int = 100
    gravity: float = 0.25
    animate: bool = True

class ResponsiveBreakpoint(BaseModel):
    min_width: int
    scaling_factor: float
    column_count: int

class PanelConfig(BaseModel):
    default_visible: bool = True
    grid_position: Optional[str]  # CSS grid-area
    min_width: str = "300px"
    max_height: str = "80vh"
    priority: int = 1  # For mobile stacking order

class InteractionSettings(BaseModel):
    drag_enabled: bool = True
    zoom_enabled: bool = True
    tooltip_delay: int = 300  # ms
    max_zoom: float = 3.0
    min_zoom: float = 0.5
    highlight_neighbors: bool = True

class FeatureFlags(BaseModel):
    enable_live_mode: bool = True
    show_debug_overlay: bool = False
    experimental_layout_engine: bool = False
    memory_visualizer: bool = False

class DisplayConfig(BaseModel):
    """
    Central configuration hub for Grace's dashboard visualization settings
    """
    theme: ThemeSettings = ThemeSettings()
    graph_layouts: Dict[str, GraphLayoutPreset] = {
        "default": GraphLayoutPreset(name="default"),
        "compact": GraphLayoutPreset(name="compact", node_spacing=40, edge_length=75),
        "hierarchical": GraphLayoutPreset(name="hierarchical", algorithm="dagre")
    }
    breakpoints: Dict[str, ResponsiveBreakpoint] = {
        "mobile": ResponsiveBreakpoint(min_width=0, scaling_factor=0.8, column_count=1),
        "tablet": ResponsiveBreakpoint(min_width=768, scaling_factor=1.0, column_count=2),
        "desktop": ResponsiveBreakpoint(min_width=1024, scaling_factor=1.2, column_count=3)
    }
    panels: Dict[str, PanelConfig] = {
        "cognitive_map": PanelConfig(grid_position="1 / 1 / 4 / 4", max_height="90vh"),
        "health_overview": PanelConfig(grid_position="1 / 4 / 2 / 5"),
        "command_console": PanelConfig(grid_position="2 / 4 / 3 / 5"),
        "memory_visualizer": PanelConfig(default_visible=False)
    }
    interactions: InteractionSettings = InteractionSettings()
    features: FeatureFlags = FeatureFlags()
    
    def get_current_breakpoint(self, viewport_width: int) -> str:
        for bp_name, bp in sorted(
            self.breakpoints.items(),
            key=lambda x: x[1].min_width,
            reverse=True
        ):
            if viewport_width >= bp.min_width:
                return bp_name
        return "mobile"
    
    def generate_css_variables(self) -> str:
        """Generates CSS variable string for current theme"""
        return f"""
            :root {{
                --grace-primary: {self.theme.colors.primary};
                --grace-secondary: {self.theme.colors.secondary};
                --grace-bg: {self.theme.colors.background};
                --grace-text: {self.theme.colors.text};
                --grace-error: {self.theme.colors.error};
                --grace-warning: {self.theme.colors.warning};
                --grace-success: {self.theme.colors.success};
                --grace-font-family: {self.theme.font_family};
                --grace-font-size: {self.theme.base_font_size};
                --grace-spacing-unit: {self.theme.spacing_unit};
                --grace-transition: all {self.theme.transition_duration} {self.theme.transition_timing};
            }}
        """
    
    def get_graph_style(self, preset_name: str = "default") -> Dict:
        """Get Cytoscape-compatible style configuration"""
        preset = self.graph_layouts.get(preset_name, self.graph_layouts["default"])
        return {
            "layout": {
                "name": preset.algorithm,
                "animate": preset.animate,
                "padding": preset.padding,
                "nodeSpacing": preset.node_spacing,
                "edgeLengthVal": preset.edge_length,
                "gravity": preset.gravity
            },
            "style": [
                {
                    "selector": "node",
                    "style": {
                        "width": 40,
                        "height": 40,
                        "backgroundColor": self.theme.colors.primary,
                        "label": "data(id)"
                    }
                },
                {
                    "selector": "edge",
                    "style": {
                        "width": 2,
                        "lineColor": self.theme.colors.secondary,
                        "curveStyle": "bezier"
                    }
                }
            ]
        }

# Initialize default configuration
active_config = DisplayConfig()

# Example usage:
# active_config.theme.mode = "dark"
# active_config.features.enable_live_mode = False