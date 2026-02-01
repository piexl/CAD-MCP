"""
Natural Language Processor Module
Parses natural language commands into CAD operations.
"""

import re
from typing import Dict, List, Tuple, Optional, Any


class NLPProcessor:
    """Natural language processor for CAD commands."""
    
    def __init__(self):
        """Initialize NLP processor with keyword mappings."""
        self.color_keywords = {
            "red", "yellow", "green", "cyan", "blue", "magenta", 
            "white", "black", "gray", "grey"
        }
        
        self.shape_keywords = {
            "line": ["line", "lines"],
            "circle": ["circle", "circles"],
            "arc": ["arc", "arcs"],
            "rectangle": ["rectangle", "rect", "box", "square"],
            "polyline": ["polyline", "polygon", "path"],
            "text": ["text", "label", "annotation"],
            "hatch": ["hatch", "fill", "pattern"],
            "dimension": ["dimension", "measure", "measurement"]
        }
        
        self.action_keywords = {
            "draw": ["draw", "create", "add", "make"],
            "save": ["save", "export", "write"]
        }
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """
        Parse a natural language command into structured parameters.
        
        Args:
            command: Natural language command string
            
        Returns:
            Dictionary with parsed command parameters
        """
        command_lower = command.lower()
        
        # Detect command type
        cmd_type = self._detect_command_type(command_lower)
        
        # Extract parameters based on command type
        if cmd_type == "save":
            return self._parse_save_command(command)
        elif cmd_type in self.shape_keywords:
            return self._parse_draw_command(command, cmd_type)
        else:
            return {"type": "unknown", "original": command}
    
    def _detect_command_type(self, command: str) -> str:
        """Detect the type of command from the text."""
        # Check for save command
        if any(keyword in command for keyword in self.action_keywords["save"]):
            return "save"
        
        # Check for shape keywords
        for shape, keywords in self.shape_keywords.items():
            if any(keyword in command for keyword in keywords):
                return shape
        
        return "unknown"
    
    def _parse_save_command(self, command: str) -> Dict[str, Any]:
        """Parse a save command."""
        # Try to extract filename
        filename_match = re.search(r'(?:as|to|in)\s+["\']?([^"\']+\.dwg)["\']?', command, re.IGNORECASE)
        
        result = {"type": "save"}
        if filename_match:
            result["filename"] = filename_match.group(1)
        
        return result
    
    def _parse_draw_command(self, command: str, shape: str) -> Dict[str, Any]:
        """Parse a drawing command."""
        result = {
            "type": "draw",
            "shape": shape,
            "color": self._extract_color(command),
            "layer": self._extract_layer(command)
        }
        
        # Extract numeric values (coordinates, dimensions, etc.)
        numbers = self._extract_numbers(command)
        
        # Parse shape-specific parameters
        if shape == "line":
            result.update(self._parse_line_params(command, numbers))
        elif shape == "circle":
            result.update(self._parse_circle_params(command, numbers))
        elif shape == "arc":
            result.update(self._parse_arc_params(command, numbers))
        elif shape == "rectangle":
            result.update(self._parse_rectangle_params(command, numbers))
        elif shape == "polyline":
            result.update(self._parse_polyline_params(command, numbers))
        elif shape == "text":
            result.update(self._parse_text_params(command, numbers))
        elif shape == "hatch":
            result.update(self._parse_hatch_params(command, numbers))
        elif shape == "dimension":
            result.update(self._parse_dimension_params(command, numbers))
        
        return result
    
    def _extract_color(self, command: str) -> Optional[str]:
        """Extract color from command text."""
        command_lower = command.lower()
        for color in self.color_keywords:
            if color in command_lower:
                return color
        return None
    
    def _extract_layer(self, command: str) -> Optional[str]:
        """Extract layer name from command text."""
        layer_match = re.search(r'(?:on|in)\s+layer\s+["\']?([^"\']+)["\']?', command, re.IGNORECASE)
        if layer_match:
            return layer_match.group(1)
        return None
    
    def _extract_numbers(self, command: str) -> List[float]:
        """Extract all numeric values from command."""
        # Find all numbers (including decimals and negatives)
        numbers = re.findall(r'-?\d+\.?\d*', command)
        return [float(n) for n in numbers]
    
    def _extract_points(self, command: str) -> List[Tuple[float, float]]:
        """Extract coordinate points from command."""
        # Look for patterns like (x,y) or x,y
        point_pattern = r'\(?(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\)?'
        matches = re.findall(point_pattern, command)
        return [(float(x), float(y)) for x, y in matches]
    
    def _parse_line_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse line-specific parameters."""
        points = self._extract_points(command)
        
        if len(points) >= 2:
            return {
                "start_point": points[0],
                "end_point": points[1]
            }
        elif len(numbers) >= 4:
            return {
                "start_point": (numbers[0], numbers[1]),
                "end_point": (numbers[2], numbers[3])
            }
        else:
            return {"error": "Insufficient coordinates for line"}
    
    def _parse_circle_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse circle-specific parameters."""
        points = self._extract_points(command)
        
        # Try to extract radius
        radius_match = re.search(r'radius\s+(-?\d+\.?\d*)', command, re.IGNORECASE)
        
        if len(points) >= 1:
            center = points[0]
            if radius_match:
                radius = float(radius_match.group(1))
            elif len(numbers) >= 3:
                radius = numbers[2]
            else:
                return {"error": "Missing radius for circle"}
            
            return {
                "center": center,
                "radius": radius
            }
        elif len(numbers) >= 3:
            return {
                "center": (numbers[0], numbers[1]),
                "radius": numbers[2]
            }
        else:
            return {"error": "Insufficient parameters for circle"}
    
    def _parse_arc_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse arc-specific parameters."""
        points = self._extract_points(command)
        
        # Try to extract angles
        start_angle_match = re.search(r'(?:start|from)\s+angle?\s+(-?\d+\.?\d*)', command, re.IGNORECASE)
        end_angle_match = re.search(r'(?:end|to)\s+angle?\s+(-?\d+\.?\d*)', command, re.IGNORECASE)
        radius_match = re.search(r'radius\s+(-?\d+\.?\d*)', command, re.IGNORECASE)
        
        if len(points) >= 1 and radius_match and start_angle_match and end_angle_match:
            return {
                "center": points[0],
                "radius": float(radius_match.group(1)),
                "start_angle": float(start_angle_match.group(1)),
                "end_angle": float(end_angle_match.group(1))
            }
        elif len(numbers) >= 5:
            # Assume format: center_x, center_y, radius, start_angle, end_angle
            return {
                "center": (numbers[0], numbers[1]),
                "radius": numbers[2],
                "start_angle": numbers[3],
                "end_angle": numbers[4]
            }
        else:
            return {"error": "Insufficient parameters for arc"}
    
    def _parse_rectangle_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse rectangle-specific parameters."""
        points = self._extract_points(command)
        
        if len(points) >= 2:
            return {
                "corner1": points[0],
                "corner2": points[1]
            }
        elif len(numbers) >= 4:
            return {
                "corner1": (numbers[0], numbers[1]),
                "corner2": (numbers[2], numbers[3])
            }
        else:
            return {"error": "Insufficient coordinates for rectangle"}
    
    def _parse_polyline_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse polyline-specific parameters."""
        points = self._extract_points(command)
        
        if len(points) >= 2:
            closed = "closed" in command.lower() or "close" in command.lower()
            return {
                "points": points,
                "closed": closed
            }
        elif len(numbers) >= 4 and len(numbers) % 2 == 0:
            # Convert flat list to point pairs
            points = [(numbers[i], numbers[i+1]) for i in range(0, len(numbers), 2)]
            closed = "closed" in command.lower() or "close" in command.lower()
            return {
                "points": points,
                "closed": closed
            }
        else:
            return {"error": "Insufficient points for polyline"}
    
    def _parse_text_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse text-specific parameters."""
        points = self._extract_points(command)
        
        # Extract text content (look for quoted strings)
        text_match = re.search(r'["\']([^"\']+)["\']', command)
        if not text_match:
            # Try to find text after "text" keyword
            text_match = re.search(r'(?:text|label)\s+(?:saying\s+)?["\']?([^"\']+?)["\']?(?:\s+at|\s+$)', command, re.IGNORECASE)
        
        # Extract height
        height_match = re.search(r'height\s+(-?\d+\.?\d*)', command, re.IGNORECASE)
        
        result = {}
        
        if text_match:
            result["text"] = text_match.group(1).strip()
        else:
            result["error"] = "No text content found"
        
        if len(points) >= 1:
            result["position"] = points[0]
        elif len(numbers) >= 2:
            result["position"] = (numbers[0], numbers[1])
        else:
            result["error"] = "No position specified for text"
        
        if height_match:
            result["height"] = float(height_match.group(1))
        
        return result
    
    def _parse_hatch_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse hatch-specific parameters."""
        points = self._extract_points(command)
        
        # Extract pattern name
        pattern_match = re.search(r'pattern\s+["\']?([^"\']+)["\']?', command, re.IGNORECASE)
        
        result = {}
        
        if len(points) >= 3:
            result["outer_loop_points"] = points
        elif len(numbers) >= 6 and len(numbers) % 2 == 0:
            points = [(numbers[i], numbers[i+1]) for i in range(0, len(numbers), 2)]
            result["outer_loop_points"] = points
        else:
            result["error"] = "Insufficient points for hatch boundary"
        
        if pattern_match:
            result["pattern_name"] = pattern_match.group(1)
        
        return result
    
    def _parse_dimension_params(self, command: str, numbers: List[float]) -> Dict[str, Any]:
        """Parse dimension-specific parameters."""
        points = self._extract_points(command)
        
        if len(points) >= 3:
            return {
                "point1": points[0],
                "point2": points[1],
                "text_position": points[2]
            }
        elif len(numbers) >= 6:
            return {
                "point1": (numbers[0], numbers[1]),
                "point2": (numbers[2], numbers[3]),
                "text_position": (numbers[4], numbers[5])
            }
        else:
            return {"error": "Insufficient points for dimension"}
