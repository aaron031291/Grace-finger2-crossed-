from typing import Literal
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, PositiveInt
from display_config import active_config

router = APIRouter(tags=["Layout Configuration"], prefix="/api/layout")

# Response Models
class LayoutPresetResponse(BaseModel):
    name: str
    algorithm: str
    node_spacing: int
    edge_length: int
    animate: bool

class CSSVariablesResponse(BaseModel):
    css: str
    content_type: str = "text/css"

class BreakpointResponse(BaseModel):
    name: str
    min_width: int
    scaling_factor: float
    column_count: int

# Preset Options Type
LayoutPreset = Literal["default", "compact", "hierarchical"]

@router.get("/preset", response_model=LayoutPresetResponse)
async def get_layout_preset(
    preset: LayoutPreset = Query(
        "default", 
        description="Layout configuration preset",
        example="compact"
    )
):
    """
    Retrieve graph layout configuration based on preset name.
    
    **Available Presets:**
    - default: Balanced spacing with organic layout
    - compact: Dense node arrangement
    - hierarchical: Top-down tree structure
    """
    try:
        config = active_config.get_graph_style(preset)
        return {
            "name": preset,
            "algorithm": config["layout"]["name"],
            "node_spacing": config["layout"]["nodeSpacing"],
            "edge_length": config["layout"]["edgeLengthVal"],
            "animate": config["layout"]["animate"]
        }
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid layout configuration: {str(e)}"
        )

@router.get("/css", response_model=CSSVariablesResponse)
async def get_css_variables():
    """Generate CSS variables for current theme configuration"""
    try:
        return CSSVariablesResponse(
            css=active_config.generate_css_variables()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"CSS generation failed: {str(e)}"
        )

@router.get("/breakpoint", response_model=BreakpointResponse)
async def get_breakpoint(
    viewport_width: PositiveInt = Query(
        ...,
        example=1440,
        description="Viewport width in pixels (>= 0)"
    )
):
    """Determine responsive layout breakpoint based on viewport width"""
    try:
        bp_name = active_config.get_current_breakpoint(viewport_width)
        bp_config = active_config.breakpoints[bp_name]
        return {
            "name": bp_name,
            "min_width": bp_config.min_width,
            "scaling_factor": bp_config.scaling_factor,
            "column_count": bp_config.column_count
        }
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Breakpoint configuration error: {str(e)}"
        )