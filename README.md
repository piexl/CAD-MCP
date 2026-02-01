# CAD-MCP Server (CAD Model Context Protocol Server)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [中文](#中文)

---

## English

### Project Introduction

CAD-MCP is an innovative CAD control service that allows controlling CAD software for drawing operations through natural language instructions. This project combines natural language processing and CAD automation technology, enabling users to create and modify CAD drawings through simple text commands without manually operating the CAD interface.

The server implements the Model Context Protocol (MCP), allowing AI assistants like Claude, Cursor, and other MCP-compatible clients to interact with CAD software seamlessly.

### Features

#### CAD Control Functions

- **Multiple CAD Software Support**: Supports mainstream CAD software including AutoCAD, GstarCAD (GCAD), and ZWCAD
- **Basic Drawing Functions**:
  - Line drawing
  - Circle drawing
  - Arc drawing
  - Rectangle drawing
  - Polyline drawing
  - Text addition
  - Pattern filling (hatch)
  - Dimension annotation
- **Layer Management**: Create and switch layers automatically
- **Drawing Save**: Save the current drawing as a DWG file

#### Natural Language Processing Functions

- **Command Parsing**: Parse natural language instructions into CAD operation parameters
- **Color Recognition**: Extract color information from text and apply it to drawing objects
- **Shape Keyword Mapping**: Support recognition of various shape description words
- **Action Keyword Mapping**: Recognize various drawing and editing actions

### Installation Requirements

#### Dependencies

```
pywin32>=301        # Windows COM interface support
mcp>=1.23.0         # Model Context Protocol library
pydantic>=2.0.0     # Data validation
```

#### System Requirements

- Windows operating system
- Installed CAD software (AutoCAD, GstarCAD, or ZWCAD)
- Python 3.8 or higher

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/piexl/CAD-MCP.git
   cd CAD-MCP
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the server by editing `src/config.json` if needed

### Configuration

The configuration file is located at `src/config.json` and contains the following main settings:

```json
{
    "server": {
        "name": "CAD MCP Server",
        "version": "1.0.0"
    },
    "cad": {
        "type": "AutoCAD",
        "startup_wait_time": 20,
        "command_delay": 0.5
    },
    "output": {
        "directory": "./output",
        "default_filename": "cad_drawing.dwg"
    }
}
```

**Configuration Options:**
- **server**: Server name and version information
- **cad**:
  - `type`: CAD software type (AutoCAD, GCAD, GstarCAD, or ZWCAD)
  - `startup_wait_time`: CAD startup waiting time in seconds
  - `command_delay`: Delay between commands in seconds
- **output**: Output file settings

### Usage

#### Starting the Service

Run the server directly:
```bash
python src/server.py
```

#### Claude Desktop Configuration

Add to your Claude Desktop configuration file (`claude_desktop_config.json`):

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

**Note**: Replace `C:\\path\\to\\CAD-MCP\\src\\server.py` with the actual path to your installation.

#### Cursor Configuration

Add to your Cursor MCP configuration:

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

#### Windsurf Configuration

Similar to Claude Desktop, add the configuration to Windsurf's MCP settings.

#### MCP Inspector (for testing)

Test the server with MCP Inspector:
```bash
npx -y @modelcontextprotocol/inspector python C:\\path\\to\\CAD-MCP\\src\\server.py
```

### API Reference

The server provides the following MCP tools:

#### Drawing Tools

1. **draw_line** - Draw a line between two points
   - Parameters: `start_x`, `start_y`, `end_x`, `end_y`, `color` (optional), `layer` (optional)

2. **draw_circle** - Draw a circle with specified center and radius
   - Parameters: `center_x`, `center_y`, `radius`, `color` (optional), `layer` (optional)

3. **draw_arc** - Draw an arc with center, radius, and angle range
   - Parameters: `center_x`, `center_y`, `radius`, `start_angle`, `end_angle`, `color` (optional), `layer` (optional)

4. **draw_rectangle** - Draw a rectangle between two corner points
   - Parameters: `corner1_x`, `corner1_y`, `corner2_x`, `corner2_y`, `color` (optional), `layer` (optional)

5. **draw_polyline** - Draw a polyline through multiple points
   - Parameters: `points` (list of tuples), `closed` (boolean), `color` (optional), `layer` (optional)

6. **draw_text** - Add text annotation to the drawing
   - Parameters: `x`, `y`, `text`, `height` (optional), `color` (optional), `layer` (optional)

7. **draw_hatch** - Create a hatch pattern within a boundary
   - Parameters: `points` (boundary), `pattern_name` (optional), `color` (optional), `layer` (optional)

8. **add_dimension** - Add a linear dimension between two points
   - Parameters: `point1_x`, `point1_y`, `point2_x`, `point2_y`, `text_x`, `text_y`, `color` (optional), `layer` (optional)

#### Utility Tools

9. **save_drawing** - Save the current drawing to a file
   - Parameters: `filename` (optional)

10. **process_command** - Process a natural language command for CAD operations
    - Parameters: `command` (string)

### Example Commands

Using natural language commands with `process_command`:

- "Draw a red line from (0,0) to (10,10)"
- "Create a blue circle at (5,5) with radius 3"
- "Draw a rectangle from (0,0) to (20,15)"
- "Add text 'Hello CAD' at (10,10)"
- "Save the drawing as my_design.dwg"

### Project Structure

```
CAD-MCP/
├── .gitignore           # Git ignore file
├── README.md            # This file
├── requirements.txt     # Project dependencies
├── imgs/                # Images and demo resources
├── output/              # Output directory for drawings
└── src/                 # Source code
    ├── __init__.py      # Package initialization
    ├── cad_controller.py # CAD controller (COM automation)
    ├── config.json      # Configuration file
    ├── nlp_processor.py # Natural language processor
    └── server.py        # MCP server implementation
```

### Troubleshooting

**Issue**: CAD software not starting
- **Solution**: Ensure CAD software is properly installed and increase `startup_wait_time` in config

**Issue**: COM errors
- **Solution**: Run Python with administrator privileges and ensure pywin32 is properly installed

**Issue**: Connection timeout
- **Solution**: Increase `startup_wait_time` in configuration file

### Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 中文

### 项目介绍

CAD-MCP 是一个创新的 CAD 控制服务，允许通过自然语言指令控制 CAD 软件进行绘图操作。该项目结合了自然语言处理和 CAD 自动化技术，使用户能够通过简单的文本命令创建和修改 CAD 图纸，而无需手动操作 CAD 界面。

该服务器实现了模型上下文协议（MCP），允许 Claude、Cursor 和其他兼容 MCP 的客户端与 CAD 软件无缝交互。

### 功能特性

#### CAD 控制功能

- **支持多种 CAD 软件**：支持主流 CAD 软件，包括 AutoCAD、GstarCAD (GCAD) 和 ZWCAD
- **基本绘图功能**：
  - 绘制直线
  - 绘制圆形
  - 绘制圆弧
  - 绘制矩形
  - 绘制多段线
  - 添加文本
  - 图案填充
  - 尺寸标注
- **图层管理**：自动创建和切换图层
- **图纸保存**：将当前图纸保存为 DWG 文件

#### 自然语言处理功能

- **命令解析**：将自然语言指令解析为 CAD 操作参数
- **颜色识别**：从文本中提取颜色信息并应用到绘图对象
- **形状关键词映射**：支持识别各种形状描述词
- **动作关键词映射**：识别各种绘图和编辑动作

### 安装要求

#### 依赖项

```
pywin32>=301        # Windows COM 接口支持
mcp>=1.23.0         # 模型上下文协议库
pydantic>=2.0.0     # 数据验证
```

#### 系统要求

- Windows 操作系统
- 已安装的 CAD 软件（AutoCAD、GstarCAD 或 ZWCAD）
- Python 3.8 或更高版本

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/piexl/CAD-MCP.git
   cd CAD-MCP
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 如需要，编辑 `src/config.json` 配置服务器

### 配置说明

配置文件位于 `src/config.json`，包含以下主要设置：

```json
{
    "server": {
        "name": "CAD MCP Server",
        "version": "1.0.0"
    },
    "cad": {
        "type": "AutoCAD",
        "startup_wait_time": 20,
        "command_delay": 0.5
    },
    "output": {
        "directory": "./output",
        "default_filename": "cad_drawing.dwg"
    }
}
```

**配置选项：**
- **server**：服务器名称和版本信息
- **cad**：
  - `type`：CAD 软件类型（AutoCAD、GCAD、GstarCAD 或 ZWCAD）
  - `startup_wait_time`：CAD 启动等待时间（秒）
  - `command_delay`：命令执行延迟（秒）
- **output**：输出文件设置

### 使用方法

#### 启动服务

直接运行服务器：
```bash
python src/server.py
```

#### Claude Desktop 配置

在 Claude Desktop 配置文件（`claude_desktop_config.json`）中添加：

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

**注意**：将 `C:\\path\\to\\CAD-MCP\\src\\server.py` 替换为实际安装路径。

### API 参考

服务器提供以下 MCP 工具：

#### 绘图工具

1. **draw_line** - 在两点之间绘制直线
2. **draw_circle** - 绘制指定中心和半径的圆
3. **draw_arc** - 绘制指定中心、半径和角度范围的圆弧
4. **draw_rectangle** - 在两个角点之间绘制矩形
5. **draw_polyline** - 通过多个点绘制多段线
6. **draw_text** - 向图纸添加文本注释
7. **draw_hatch** - 在边界内创建填充图案
8. **add_dimension** - 在两点之间添加线性尺寸标注

#### 实用工具

9. **save_drawing** - 将当前图纸保存到文件
10. **process_command** - 处理自然语言 CAD 操作命令

### 示例命令

使用 `process_command` 的自然语言命令：

- "从 (0,0) 到 (10,10) 画一条红线"
- "在 (5,5) 处创建一个半径为 3 的蓝色圆"
- "从 (0,0) 到 (20,15) 画一个矩形"
- "在 (10,10) 处添加文本 'Hello CAD'"
- "将图纸保存为 my_design.dwg"

### 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。
