# Quick Start Guide for CAD-MCP

This guide will help you get started with CAD-MCP quickly.

## Prerequisites

1. **Windows OS**: CAD-MCP uses Windows COM automation
2. **CAD Software**: Install one of the following:
   - AutoCAD
   - GstarCAD (GCAD)
   - ZWCAD
3. **Python**: Python 3.8 or higher

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/piexl/CAD-MCP.git
cd CAD-MCP
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure CAD Software

Edit `src/config.json` to match your CAD software:

```json
{
    "cad": {
        "type": "AutoCAD"    // Change to "GCAD", "GstarCAD", or "ZWCAD" if needed
    }
}
```

### 4. Test the Server

Run the test script to verify NLP processing:

```bash
python test_nlp.py
```

## Using with Claude Desktop

1. Locate your Claude Desktop config file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the CAD-MCP server configuration:

```json
{
    "mcpServers": {
        "CAD": {
            "command": "python",
            "args": [
                "C:\\path\\to\\CAD-MCP\\src\\server.py"
            ]
        }
    }
}
```

**Important**: Replace `C:\\path\\to\\CAD-MCP` with your actual installation path. Use double backslashes (`\\`) on Windows.

3. Restart Claude Desktop

4. Look for the 🔌 icon to verify the CAD server is connected

## Using with Cursor

1. Open Cursor Settings
2. Navigate to MCP (Model Context Protocol) configuration
3. Add the server configuration as shown above
4. Restart Cursor

## Try Your First Commands

Once connected, try these commands in Claude or Cursor:

### Basic Drawing
```
Draw a red line from (0,0) to (10,10)
```

### Creating Shapes
```
Create a blue circle at (5,5) with radius 3
```

### Complex Drawings
```
Draw a rectangle from (0,0) to (20,15)
Add text "My Drawing" at (10,12)
Save the drawing as test.dwg
```

## Tips

- **CAD must be running**: The server will try to connect to an existing CAD instance or start a new one
- **Administrator privileges**: You may need to run Python/your editor as administrator
- **First connection is slow**: The first time connecting may take 20-30 seconds
- **Check the output directory**: Saved drawings are stored in `./output/` by default

## Troubleshooting

### "Failed to connect to CAD"
- Ensure CAD software is installed
- Run Python/editor as administrator
- Increase `startup_wait_time` in `src/config.json`

### "pywin32 not installed"
```bash
pip install pywin32>=301
```

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### COM errors
- Close all CAD instances and try again
- Check Windows Event Viewer for COM-related errors
- Reinstall pywin32:
  ```bash
  pip uninstall pywin32
  pip install pywin32>=301
  ```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [EXAMPLES.md](EXAMPLES.md) for more command examples
- Explore all available tools in the server

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the full documentation in README.md
3. Open an issue on GitHub with:
   - Your error message
   - CAD software version
   - Python version
   - Steps to reproduce
