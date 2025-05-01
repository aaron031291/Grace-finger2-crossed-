from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from display_config import active_config

router = APIRouter()

# Response Models
class ThemeResponse(BaseModel):
    mode: str
    colors: dict
    font_settings: dict

class PanelVisibilityResponse(BaseModel):
    visible_panels: dict
    layout_map: dict

class LayoutStyleResponse(BaseModel):
    breakpoints: dict
    graph_style: dict
    css_vars: str

@router.get("/api/interface/theme", response_model=ThemeResponse)
async def get_theme_mode():
    """Get current theme configuration"""
    try:
        return {
            "mode": active_config.theme.mode,
            "colors": active_config.theme.colors.dict(),
            "font_settings": {
                "family": active_config.theme.font_family,
                "size": active_config.theme.base_font_size
            }
        }
    except AttributeError as e:
        raise HTTPException(500, f"Theme configuration error: {str(e)}")

@router.get("/api/interface/panels", response_model=PanelVisibilityResponse)
async def get_visible_panels():
    """Get panel visibility and layout positions"""
    try:
        return {
            "visible_panels": {k: v.default_visible for k, v in active_config.panels.items()},
            "layout_map": {k: v.dict() for k, v in active_config.panels.items()}
        }
    except AttributeError as e:
        raise HTTPException(500, f"Panel configuration error: {str(e)}")

@router.get("/api/interface/layout", response_model=LayoutStyleResponse)
async def get_layout_styles(preset: str = "default"):
    """Get layout configuration with optional preset selection"""
    try:
        return {
            "breakpoints": {k: v.dict() for k, v in active_config.breakpoints.items()},
            "graph_style": active_config.get_graph_style(preset),
            "css_vars": active_config.generate_css_variables()
        }
    except KeyError:
        raise HTTPException(400, f"Invalid layout preset: {preset}")
    except Exception as e:
        raise HTTPException(500, f"Layout configuration error: {str(e)}")