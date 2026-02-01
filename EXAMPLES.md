# CAD-MCP Example Commands

This file contains example commands that can be used with the CAD-MCP server.

## Direct API Calls (through MCP tools)

### Drawing Lines
```json
{
    "tool": "draw_line",
    "arguments": {
        "start_x": 0,
        "start_y": 0,
        "end_x": 10,
        "end_y": 10,
        "color": "red"
    }
}
```

### Drawing Circles
```json
{
    "tool": "draw_circle",
    "arguments": {
        "center_x": 5,
        "center_y": 5,
        "radius": 3,
        "color": "blue"
    }
}
```

### Drawing Rectangles
```json
{
    "tool": "draw_rectangle",
    "arguments": {
        "corner1_x": 0,
        "corner1_y": 0,
        "corner2_x": 20,
        "corner2_y": 15,
        "color": "green"
    }
}
```

### Adding Text
```json
{
    "tool": "draw_text",
    "arguments": {
        "x": 10,
        "y": 10,
        "text": "Hello CAD",
        "height": 3,
        "color": "black"
    }
}
```

## Natural Language Commands (through process_command)

### Basic Shapes
- "Draw a red line from (0,0) to (10,10)"
- "Create a blue circle at (5,5) with radius 3"
- "Draw a green rectangle from (0,0) to (20,15)"
- "Make a yellow arc at (10,10) with radius 5 from angle 0 to angle 90"

### Polylines
- "Draw a polyline through (0,0), (5,5), (10,0), (15,5)"
- "Create a closed polyline through (0,0), (10,0), (10,10), (0,10)"

### Text and Annotations
- "Add text 'Hello CAD' at (10,10)"
- "Add text 'Building A' at (5,5) with height 5"

### Dimensions
- "Add dimension from (0,0) to (10,0) at text position (5,2)"

### Saving
- "Save the drawing"
- "Save the drawing as my_design.dwg"

## Example Session

1. Start with a rectangle base:
   - "Draw a rectangle from (0,0) to (20,20)"

2. Add a circle in the center:
   - "Draw a blue circle at (10,10) with radius 5"

3. Add text label:
   - "Add text 'Circle' at (10,15)"

4. Save the result:
   - "Save the drawing as example.dwg"
