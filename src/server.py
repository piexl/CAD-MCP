"""
MCP Server Implementation
Provides Model Context Protocol interface for CAD control.
"""

import asyncio
import json
import sys
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

from cad_controller import CADController
from nlp_processor import NLPProcessor


# Define input models for each tool
class LineInput(BaseModel):
    start_x: float = Field(description="X coordinate of start point")
    start_y: float = Field(description="Y coordinate of start point")
    end_x: float = Field(description="X coordinate of end point")
    end_y: float = Field(description="Y coordinate of end point")
    color: Optional[str] = Field(default=None, description="Color name (red, blue, green, etc.)")
    layer: Optional[str] = Field(default=None, description="Layer name")


class CircleInput(BaseModel):
    center_x: float = Field(description="X coordinate of circle center")
    center_y: float = Field(description="Y coordinate of circle center")
    radius: float = Field(description="Circle radius")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class ArcInput(BaseModel):
    center_x: float = Field(description="X coordinate of arc center")
    center_y: float = Field(description="Y coordinate of arc center")
    radius: float = Field(description="Arc radius")
    start_angle: float = Field(description="Start angle in degrees")
    end_angle: float = Field(description="End angle in degrees")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class RectangleInput(BaseModel):
    corner1_x: float = Field(description="X coordinate of first corner")
    corner1_y: float = Field(description="Y coordinate of first corner")
    corner2_x: float = Field(description="X coordinate of opposite corner")
    corner2_y: float = Field(description="Y coordinate of opposite corner")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class PolylineInput(BaseModel):
    points: list[tuple[float, float]] = Field(description="List of (x, y) coordinate tuples")
    closed: bool = Field(default=False, description="Whether to close the polyline")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class TextInput(BaseModel):
    x: float = Field(description="X coordinate of text position")
    y: float = Field(description="Y coordinate of text position")
    text: str = Field(description="Text content to add")
    height: float = Field(default=2.5, description="Text height")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class HatchInput(BaseModel):
    points: list[tuple[float, float]] = Field(description="Boundary points for hatch")
    pattern_name: str = Field(default="ANSI31", description="Hatch pattern name")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class DimensionInput(BaseModel):
    point1_x: float = Field(description="X coordinate of first point")
    point1_y: float = Field(description="Y coordinate of first point")
    point2_x: float = Field(description="X coordinate of second point")
    point2_y: float = Field(description="Y coordinate of second point")
    text_x: float = Field(description="X coordinate of dimension text position")
    text_y: float = Field(description="Y coordinate of dimension text position")
    color: Optional[str] = Field(default=None, description="Color name")
    layer: Optional[str] = Field(default=None, description="Layer name")


class SaveInput(BaseModel):
    filename: Optional[str] = Field(default=None, description="Output filename (optional)")


class CommandInput(BaseModel):
    command: str = Field(description="Natural language command for CAD operations")


# Initialize CAD controller and NLP processor
cad_controller = CADController()
nlp_processor = NLPProcessor()

# Create MCP server instance
app = Server("cad-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available CAD tools."""
    return [
        Tool(
            name="draw_line",
            description="Draw a line between two points in CAD",
            inputSchema=LineInput.model_json_schema()
        ),
        Tool(
            name="draw_circle",
            description="Draw a circle with specified center and radius",
            inputSchema=CircleInput.model_json_schema()
        ),
        Tool(
            name="draw_arc",
            description="Draw an arc with center, radius, and angle range",
            inputSchema=ArcInput.model_json_schema()
        ),
        Tool(
            name="draw_rectangle",
            description="Draw a rectangle between two corner points",
            inputSchema=RectangleInput.model_json_schema()
        ),
        Tool(
            name="draw_polyline",
            description="Draw a polyline through multiple points",
            inputSchema=PolylineInput.model_json_schema()
        ),
        Tool(
            name="draw_text",
            description="Add text annotation to the drawing",
            inputSchema=TextInput.model_json_schema()
        ),
        Tool(
            name="draw_hatch",
            description="Create a hatch pattern within a boundary",
            inputSchema=HatchInput.model_json_schema()
        ),
        Tool(
            name="add_dimension",
            description="Add a linear dimension between two points",
            inputSchema=DimensionInput.model_json_schema()
        ),
        Tool(
            name="save_drawing",
            description="Save the current drawing to a file",
            inputSchema=SaveInput.model_json_schema()
        ),
        Tool(
            name="process_command",
            description="Process a natural language command for CAD operations",
            inputSchema=CommandInput.model_json_schema()
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "draw_line":
            args = LineInput(**arguments)
            result = cad_controller.draw_line(
                start_point=(args.start_x, args.start_y),
                end_point=(args.end_x, args.end_y),
                color=args.color,
                layer=args.layer
            )
            
        elif name == "draw_circle":
            args = CircleInput(**arguments)
            result = cad_controller.draw_circle(
                center=(args.center_x, args.center_y),
                radius=args.radius,
                color=args.color,
                layer=args.layer
            )
            
        elif name == "draw_arc":
            args = ArcInput(**arguments)
            result = cad_controller.draw_arc(
                center=(args.center_x, args.center_y),
                radius=args.radius,
                start_angle=args.start_angle,
                end_angle=args.end_angle,
                color=args.color,
                layer=args.layer
            )
            
        elif name == "draw_rectangle":
            args = RectangleInput(**arguments)
            result = cad_controller.draw_rectangle(
                corner1=(args.corner1_x, args.corner1_y),
                corner2=(args.corner2_x, args.corner2_y),
                color=args.color,
                layer=args.layer
            )
            
        elif name == "draw_polyline":
            args = PolylineInput(**arguments)
            result = cad_controller.draw_polyline(
                points=args.points,
                closed=args.closed,
                color=args.color,
                layer=args.layer
            )
            
        elif name == "draw_text":
            args = TextInput(**arguments)
            result = cad_controller.draw_text(
                position=(args.x, args.y),
                text=args.text,
                height=args.height,
                color=args.color,
                layer=args.layer
            )
            
        elif name == "draw_hatch":
            args = HatchInput(**arguments)
            result = cad_controller.draw_hatch(
                outer_loop_points=args.points,
                pattern_name=args.pattern_name,
                color=args.color,
                layer=args.layer
            )
            
        elif name == "add_dimension":
            args = DimensionInput(**arguments)
            result = cad_controller.add_dimension(
                point1=(args.point1_x, args.point1_y),
                point2=(args.point2_x, args.point2_y),
                text_position=(args.text_x, args.text_y),
                color=args.color,
                layer=args.layer
            )
            
        elif name == "save_drawing":
            args = SaveInput(**arguments)
            result = cad_controller.save_drawing(filename=args.filename)
            
        elif name == "process_command":
            args = CommandInput(**arguments)
            result = await process_natural_language_command(args.command)
            
        else:
            result = f"Unknown tool: {name}"
        
        return [TextContent(type="text", text=str(result))]
        
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def process_natural_language_command(command: str) -> str:
    """Process a natural language command."""
    try:
        # Parse the command
        parsed = nlp_processor.parse_command(command)
        
        if parsed.get("type") == "unknown":
            return f"Could not understand command: {command}"
        
        if "error" in parsed:
            return f"Error parsing command: {parsed['error']}"
        
        # Execute based on parsed command
        if parsed["type"] == "save":
            return cad_controller.save_drawing(parsed.get("filename"))
        
        elif parsed["type"] == "draw":
            shape = parsed["shape"]
            color = parsed.get("color")
            layer = parsed.get("layer")
            
            if shape == "line":
                if "start_point" not in parsed or "end_point" not in parsed:
                    return "Missing coordinates for line"
                return cad_controller.draw_line(
                    parsed["start_point"], parsed["end_point"], color, layer
                )
            
            elif shape == "circle":
                if "center" not in parsed or "radius" not in parsed:
                    return "Missing parameters for circle"
                return cad_controller.draw_circle(
                    parsed["center"], parsed["radius"], color, layer
                )
            
            elif shape == "arc":
                if any(k not in parsed for k in ["center", "radius", "start_angle", "end_angle"]):
                    return "Missing parameters for arc"
                return cad_controller.draw_arc(
                    parsed["center"], parsed["radius"],
                    parsed["start_angle"], parsed["end_angle"], color, layer
                )
            
            elif shape == "rectangle":
                if "corner1" not in parsed or "corner2" not in parsed:
                    return "Missing coordinates for rectangle"
                return cad_controller.draw_rectangle(
                    parsed["corner1"], parsed["corner2"], color, layer
                )
            
            elif shape == "polyline":
                if "points" not in parsed:
                    return "Missing points for polyline"
                return cad_controller.draw_polyline(
                    parsed["points"], parsed.get("closed", False), color, layer
                )
            
            elif shape == "text":
                if "position" not in parsed or "text" not in parsed:
                    return "Missing parameters for text"
                return cad_controller.draw_text(
                    parsed["position"], parsed["text"],
                    parsed.get("height", 2.5), color, layer
                )
            
            elif shape == "hatch":
                if "outer_loop_points" not in parsed:
                    return "Missing boundary points for hatch"
                return cad_controller.draw_hatch(
                    parsed["outer_loop_points"],
                    parsed.get("pattern_name", "ANSI31"), color, layer
                )
            
            elif shape == "dimension":
                if any(k not in parsed for k in ["point1", "point2", "text_position"]):
                    return "Missing points for dimension"
                return cad_controller.add_dimension(
                    parsed["point1"], parsed["point2"],
                    parsed["text_position"], color, layer
                )
        
        return f"Processed command: {command}"
        
    except Exception as e:
        return f"Error processing command: {str(e)}"


async def main():
    """Main entry point for the server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
