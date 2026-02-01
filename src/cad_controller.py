"""
CAD Controller Module
Handles interaction with CAD software (AutoCAD, GstarCAD, ZWCAD) via COM interface.
"""

import time
import os
import json
from typing import Optional, Tuple, List
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False


class CADController:
    """Controller for CAD software operations via COM interface."""
    
    def __init__(self, config_path: str = "src/config.json"):
        """Initialize CAD controller with configuration."""
        self.config = self._load_config(config_path)
        self.cad_type = self.config["cad"]["type"]
        self.startup_wait_time = self.config["cad"]["startup_wait_time"]
        self.command_delay = self.config["cad"]["command_delay"]
        self.acad_app = None
        self.doc = None
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration if file not found
            return {
                "server": {"name": "CAD MCP Server", "version": "1.0.0"},
                "cad": {"type": "AutoCAD", "startup_wait_time": 20, "command_delay": 0.5},
                "output": {"directory": "./output", "default_filename": "cad_drawing.dwg"}
            }
    
    def connect(self) -> bool:
        """Connect to CAD application."""
        if not WIN32COM_AVAILABLE:
            raise ImportError("pywin32 is required for CAD operations. Please install it on Windows.")
        
        try:
            pythoncom.CoInitialize()
            
            # Try to get existing instance first
            prog_id_map = {
                "AutoCAD": "AutoCAD.Application",
                "GCAD": "GstarCAD.Application",
                "GstarCAD": "GstarCAD.Application",
                "ZWCAD": "ZWCAD.Application"
            }
            
            prog_id = prog_id_map.get(self.cad_type, "AutoCAD.Application")
            
            try:
                self.acad_app = win32com.client.GetActiveObject(prog_id)
            except:
                # If no active instance, create new one
                self.acad_app = win32com.client.Dispatch(prog_id)
                time.sleep(self.startup_wait_time)
            
            self.acad_app.Visible = True
            self.doc = self.acad_app.ActiveDocument
            
            if self.doc is None:
                # Create new document if none exists
                self.doc = self.acad_app.Documents.Add()
                
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {self.cad_type}: {str(e)}")
    
    def disconnect(self):
        """Disconnect from CAD application."""
        self.doc = None
        self.acad_app = None
        if WIN32COM_AVAILABLE:
            pythoncom.CoUninitialize()
    
    def _ensure_connected(self):
        """Ensure CAD connection is active."""
        if self.acad_app is None or self.doc is None:
            self.connect()
    
    def _parse_color(self, color: Optional[str]) -> int:
        """Parse color string to AutoCAD color index."""
        color_map = {
            "red": 1,
            "yellow": 2,
            "green": 3,
            "cyan": 4,
            "blue": 5,
            "magenta": 6,
            "white": 7,
            "gray": 8,
            "grey": 8,
            "black": 0
        }
        
        if color is None:
            return 7  # Default to white
        
        return color_map.get(color.lower(), 7)
    
    def draw_line(self, start_point: Tuple[float, float], end_point: Tuple[float, float], 
                  color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Draw a line in CAD."""
        self._ensure_connected()
        
        try:
            # Convert 2D points to 3D (add z=0)
            start_3d = (start_point[0], start_point[1], 0.0)
            end_3d = (end_point[0], end_point[1], 0.0)
            
            model_space = self.doc.ModelSpace
            line = model_space.AddLine(start_3d, end_3d)
            
            if color:
                line.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                line.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Line drawn from {start_point} to {end_point}"
            
        except Exception as e:
            return f"Error drawing line: {str(e)}"
    
    def draw_circle(self, center: Tuple[float, float], radius: float, 
                    color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Draw a circle in CAD."""
        self._ensure_connected()
        
        try:
            center_3d = (center[0], center[1], 0.0)
            
            model_space = self.doc.ModelSpace
            circle = model_space.AddCircle(center_3d, radius)
            
            if color:
                circle.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                circle.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Circle drawn at {center} with radius {radius}"
            
        except Exception as e:
            return f"Error drawing circle: {str(e)}"
    
    def draw_arc(self, center: Tuple[float, float], radius: float, 
                 start_angle: float, end_angle: float,
                 color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Draw an arc in CAD."""
        self._ensure_connected()
        
        try:
            import math
            center_3d = (center[0], center[1], 0.0)
            # Convert degrees to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            model_space = self.doc.ModelSpace
            arc = model_space.AddArc(center_3d, radius, start_rad, end_rad)
            
            if color:
                arc.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                arc.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Arc drawn at {center} with radius {radius}, from {start_angle}° to {end_angle}°"
            
        except Exception as e:
            return f"Error drawing arc: {str(e)}"
    
    def draw_rectangle(self, corner1: Tuple[float, float], corner2: Tuple[float, float],
                       color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Draw a rectangle using polyline."""
        self._ensure_connected()
        
        try:
            # Create rectangle points
            x1, y1 = corner1
            x2, y2 = corner2
            
            points = [
                x1, y1, 0.0,
                x2, y1, 0.0,
                x2, y2, 0.0,
                x1, y2, 0.0
            ]
            
            model_space = self.doc.ModelSpace
            polyline = model_space.AddPolyline(points)
            polyline.Closed = True
            
            if color:
                polyline.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                polyline.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Rectangle drawn from {corner1} to {corner2}"
            
        except Exception as e:
            return f"Error drawing rectangle: {str(e)}"
    
    def draw_polyline(self, points: List[Tuple[float, float]], closed: bool = False,
                      color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Draw a polyline through multiple points."""
        self._ensure_connected()
        
        try:
            # Convert 2D points to flat 3D array
            points_3d = []
            for point in points:
                points_3d.extend([point[0], point[1], 0.0])
            
            model_space = self.doc.ModelSpace
            polyline = model_space.AddPolyline(points_3d)
            polyline.Closed = closed
            
            if color:
                polyline.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                polyline.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Polyline drawn through {len(points)} points"
            
        except Exception as e:
            return f"Error drawing polyline: {str(e)}"
    
    def draw_text(self, position: Tuple[float, float], text: str, height: float = 2.5,
                  color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Add text to the drawing."""
        self._ensure_connected()
        
        try:
            position_3d = (position[0], position[1], 0.0)
            
            model_space = self.doc.ModelSpace
            text_obj = model_space.AddText(text, position_3d, height)
            
            if color:
                text_obj.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                text_obj.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Text '{text}' added at {position}"
            
        except Exception as e:
            return f"Error adding text: {str(e)}"
    
    def draw_hatch(self, outer_loop_points: List[Tuple[float, float]], 
                   pattern_name: str = "ANSI31",
                   color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Draw a hatch pattern."""
        self._ensure_connected()
        
        try:
            # Create a closed polyline for the boundary
            points_3d = []
            for point in outer_loop_points:
                points_3d.extend([point[0], point[1], 0.0])
            
            model_space = self.doc.ModelSpace
            
            # Create boundary polyline
            boundary = model_space.AddPolyline(points_3d)
            boundary.Closed = True
            
            # Create hatch
            hatch = model_space.AddHatch(0, pattern_name, True)  # 0 = acHatchPatternTypeUserDefined
            hatch.AppendOuterLoop([boundary])
            hatch.Evaluate()
            
            if color:
                hatch.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                hatch.Layer = layer
            
            # Optionally delete the boundary
            # boundary.Delete()
            
            time.sleep(self.command_delay)
            return f"Hatch pattern '{pattern_name}' created"
            
        except Exception as e:
            return f"Error creating hatch: {str(e)}"
    
    def add_dimension(self, point1: Tuple[float, float], point2: Tuple[float, float],
                      text_position: Tuple[float, float],
                      color: Optional[str] = None, layer: Optional[str] = None) -> str:
        """Add a linear dimension."""
        self._ensure_connected()
        
        try:
            point1_3d = (point1[0], point1[1], 0.0)
            point2_3d = (point2[0], point2[1], 0.0)
            text_pos_3d = (text_position[0], text_position[1], 0.0)
            
            model_space = self.doc.ModelSpace
            dimension = model_space.AddDimAligned(point1_3d, point2_3d, text_pos_3d)
            
            if color:
                dimension.Color = self._parse_color(color)
            
            if layer:
                self._create_layer_if_needed(layer)
                dimension.Layer = layer
            
            time.sleep(self.command_delay)
            return f"Dimension added between {point1} and {point2}"
            
        except Exception as e:
            return f"Error adding dimension: {str(e)}"
    
    def _create_layer_if_needed(self, layer_name: str):
        """Create a layer if it doesn't exist."""
        try:
            layers = self.doc.Layers
            try:
                # Try to get the layer
                layer = layers.Item(layer_name)
            except:
                # Layer doesn't exist, create it
                layer = layers.Add(layer_name)
        except Exception as e:
            pass  # Ignore layer creation errors
    
    def save_drawing(self, filename: Optional[str] = None) -> str:
        """Save the current drawing."""
        self._ensure_connected()
        
        try:
            if filename is None:
                output_dir = self.config["output"]["directory"]
                filename = self.config["output"]["default_filename"]
                filepath = os.path.join(output_dir, filename)
            else:
                filepath = filename
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(filepath) or "."
            os.makedirs(output_dir, exist_ok=True)
            
            # Get absolute path
            filepath = os.path.abspath(filepath)
            
            # Save the document
            self.doc.SaveAs(filepath)
            
            return f"Drawing saved to {filepath}"
            
        except Exception as e:
            return f"Error saving drawing: {str(e)}"
