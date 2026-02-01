# Contributing to CAD-MCP

Thank you for your interest in contributing to CAD-MCP! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful and constructive in all interactions with the project and community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, CAD software version)
- Any relevant error messages or logs

### Suggesting Enhancements

Feature requests are welcome! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- How it might work

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Testing

- Test your changes with at least one CAD software
- Verify NLP parsing works for new command types
- Ensure backward compatibility

### Documentation

- Update README.md if you add new features
- Add examples to EXAMPLES.md for new functionality
- Update QUICKSTART.md if setup process changes
- Include docstrings in your code

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters
- Add details in the commit body if needed

Example:
```
Add support for ellipse drawing

- Implement draw_ellipse method in CADController
- Add ellipse parsing to NLPProcessor
- Register ellipse tool in MCP server
- Update documentation with ellipse examples
```

## Project Structure

```
CAD-MCP/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── cad_controller.py    # CAD COM automation
│   ├── nlp_processor.py     # Natural language parsing
│   ├── server.py            # MCP server implementation
│   └── config.json          # Configuration
├── README.md                # Main documentation
├── QUICKSTART.md           # Quick start guide
├── EXAMPLES.md             # Usage examples
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT License
└── requirements.txt        # Dependencies
```

## Adding New CAD Operations

To add a new drawing operation:

1. **Add method to CADController** (`src/cad_controller.py`):
   ```python
   def draw_your_shape(self, params, color=None, layer=None):
       self._ensure_connected()
       # Implement drawing logic
       return "Shape drawn successfully"
   ```

2. **Add parsing to NLPProcessor** (`src/nlp_processor.py`):
   ```python
   def _parse_your_shape_params(self, command, numbers):
       # Extract parameters from natural language
       return {"param1": value1, "param2": value2}
   ```

3. **Add tool to MCP server** (`src/server.py`):
   ```python
   Tool(
       name="draw_your_shape",
       description="Draw your shape",
       inputSchema=YourShapeInput.model_json_schema()
   )
   ```

4. **Update documentation**:
   - Add to README.md API reference
   - Add examples to EXAMPLES.md

## Testing Checklist

Before submitting a PR:

- [ ] Code passes Python syntax check (`python -m py_compile`)
- [ ] New features are documented
- [ ] Examples are provided
- [ ] Tested with at least one CAD software
- [ ] No security vulnerabilities introduced
- [ ] Backwards compatible (or clearly noted if not)

## Getting Help

If you need help:
- Open an issue with your question
- Tag it with "question" label
- Provide context about what you're trying to do

## Recognition

All contributors will be recognized in the project. Thank you for helping make CAD-MCP better!
