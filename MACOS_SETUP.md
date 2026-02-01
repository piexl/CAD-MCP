# macOS 设置指南

## 项目已完成 macOS 适配！✅

这个项目已从仅支持 Windows (Win32COM) 改为支持 **macOS、Linux 和 Windows** 的跨平台解决方案。

---

## 快速开始

### 1️⃣ 安装依赖

```bash
cd /Users/kermit/codes/labs/CAD-MCP
pip install -r requirements.txt
```

**主要依赖：**
- `ezdxf>=1.0.0` - 跨平台 CAD 库（macOS/Linux 主用）
- `mcp>=0.1.0` - Model Context Protocol
- `pydantic>=2.0.0` - 数据验证

### 2️⃣ 验证安装

```bash
python -c "from src.cad_controller import CADController; c = CADController(); print('✅ 成功')"
```

### 3️⃣ 启动 MCP 服务

```bash
python src/server.py
```

---

## 配置文件

**位置：** [src/config.json](src/config.json)

### macOS 推荐配置

```json
{
    "server": {
        "name": "CAD MCP 服务器",
        "version": "1.0.0"
    },
    "cad": {
        "type": "ezdxf",  # ← 自动检测后端
        "startup_wait_time": 20,
        "command_delay": 0.5
    },
    "output": {
        "directory": "./output",
        "default_filename": "cad_drawing.dwg"
    }
}
```

---

## 与 Claude Desktop / Windsurf 集成

### 修改配置文件

编辑 `~/Library/Application\ Support/Claude/claude_desktop_config.json`：

```json
{
    "mcpServers": {
        "CAD": {
            "command": "python",
            "args": ["/Users/kermit/codes/labs/CAD-MCP/src/server.py"]
        }
    }
}
```

**注意：** 请将路径替换为你实际的项目路径。

### Windsurf 配置

编辑 `~/.windsurf/mcp_config.json`：

```json
{
    "mcpServers": {
        "CAD": {
            "command": "python",
            "args": ["/Users/kermit/codes/labs/CAD-MCP/src/server.py"]
        }
    }
}
```

---

## 功能说明

### 支持的绘图操作

✅ **基础绘图**
- `draw_line()` - 直线
- `draw_circle()` - 圆形
- `draw_arc()` - 圆弧
- `draw_rectangle()` - 矩形
- `draw_polyline()` - 多段线
- `draw_text()` - 文本
- `draw_hatch()` - 填充图案
- `add_dimension()` - 尺寸标注

✅ **图层管理**
- `create_layer()` - 创建图层

✅ **文件操作**
- `save_drawing()` - 保存为 DWG 文件

### 输出文件

绘图会自动保存为 DWG 文件，位置：`./output/cad_drawing.dwg`

---

## 后端说明

### ezdxf (跨平台)

**优点：**
- ✅ macOS、Linux、Windows 都支持
- ✅ 无需外部 CAD 软件
- ✅ 直接生成标准 DWG/DXF 文件

**缺点：**
- 不能控制已安装的 CAD 软件（如 AutoCAD）

### Win32COM (仅 Windows)

**优点：**
- ✅ 可控制已安装的 CAD 软件（AutoCAD、GstarCAD 等）
- ✅ 实时交互

**缺点：**
- ❌ 仅限 Windows 平台
- ❌ 需要安装 pywin32

---

## 故障排除

### 问题 1：导入错误

```
ModuleNotFoundError: No module named 'ezdxf'
```

**解决方案：**
```bash
pip install ezdxf
```

### 问题 2：字体警告

```
cannot load OS/2 table of font
```

这是 ezdxf 的正常警告，不影响功能。

### 问题 3：权限问题

```
PermissionError: output directory
```

**解决方案：**
```bash
mkdir -p ./output
chmod 755 ./output
```

---

## 与原项目的区别

| 功能 | 原项目 | 新版 macOS |
|-----|-------|----------|
| **Windows 支持** | ✅ COM 实时控制 | ✅ 两种后端可选 |
| **macOS 支持** | ❌ 不支持 | ✅ 完全支持 |
| **Linux 支持** | ❌ 不支持 | ✅ 完全支持 |
| **外部 CAD 依赖** | ✅ 需要 AutoCAD 等 | ❌ ezdxf 自足 |
| **DWG 输出** | ✅ (通过 CAD) | ✅ (直接生成) |
| **自然语言处理** | ✅ | ✅ |

---

## 开发者说明

### 切换后端 (高级)

代码会自动检测平台并选择合适的后端：

```python
from src.cad_controller import CADController

cad = CADController()

if cad.use_ezdxf:
    print("使用 ezdxf 后端（跨平台）")
else:
    print("使用 Win32COM 后端（Windows）")
```

### 项目结构

```
CAD-MCP/
├── src/
│   ├── cad_controller.py          # 主控制器 (跨平台)
│   ├── cad_controller_win32com_backup.py  # 原始 Windows 版本
│   ├── nlp_processor.py           # 自然语言处理
│   ├── server.py                  # MCP 服务器
│   └── config.json                # 配置文件
├── output/                        # DWG 输出目录
├── requirements.txt               # 依赖列表
└── MACOS_SETUP.md                 # 本文件
```

---

## 常见命令

### 测试绘图功能

```python
from src.cad_controller import CADController

cad = CADController()
cad.start_cad()

# 绘制一个圆
cad.draw_circle((0, 0, 0), 10, layer="geometry", color=1)

# 绘制一条直线
cad.draw_line((0, 0, 0), (20, 20, 0), layer="lines")

# 保存文件
cad.save_drawing("/tmp/test.dwg")

cad.close()
```

### 使用 MCP Inspector 测试 (推荐)

```bash
npx -y @modelcontextprotocol/inspector python /Users/kermit/codes/labs/CAD-MCP/src/server.py
```

---

## 许可证

MIT License

---

## 更新日志

### v1.1.0 (macOS 适配版)
- ✨ 添加跨平台支持（macOS/Linux/Windows）
- ✨ 集成 ezdxf 库用于文件生成
- 🔧 保留 Win32COM 支持（仅 Windows）
- 📝 更新配置文件
- 📚 添加 macOS 设置文档

---

需要帮助？查看 [README_zh.md](README_zh.md) 或 [README.md](README.md)
