import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from mcp.server import FastMCP

from cad_controller import CADController

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp_cad_server")

mcp = FastMCP(name="CAD MCP Server")

_cad: Optional[CADController] = None


def _get_cad() -> CADController:
    global _cad
    if _cad is None:
        _cad = CADController()
        started = _cad.start_cad()
        if not started:
            raise RuntimeError("CAD 启动失败")
    return _cad


def _as_point(point: Union[List[float], Tuple[float, float, float]]) -> Tuple[float, float, float]:
    if len(point) == 2:
        return (float(point[0]), float(point[1]), 0.0)
    return (float(point[0]), float(point[1]), float(point[2]))


@mcp.tool(description="绘制直线。参数: start_point, end_point, layer?, color?, lineweight?")
def draw_line(
    start_point: List[float],
    end_point: List[float],
    layer: Optional[str] = None,
    color: Optional[int] = None,
    lineweight: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    result = cad.draw_line(_as_point(start_point), _as_point(end_point), layer, color, lineweight)
    return {"ok": result is not None}


@mcp.tool(description="绘制圆。参数: center, radius, layer?, color?, lineweight?")
def draw_circle(
    center: List[float],
    radius: float,
    layer: Optional[str] = None,
    color: Optional[int] = None,
    lineweight: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    result = cad.draw_circle(_as_point(center), float(radius), layer, color, lineweight)
    return {"ok": result is not None}


@mcp.tool(description="绘制圆弧。参数: center, radius, start_angle, end_angle, layer?, color?, lineweight?")
def draw_arc(
    center: List[float],
    radius: float,
    start_angle: float,
    end_angle: float,
    layer: Optional[str] = None,
    color: Optional[int] = None,
    lineweight: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    result = cad.draw_arc(_as_point(center), float(radius), float(start_angle), float(end_angle), layer, color, lineweight)
    return {"ok": result is not None}


@mcp.tool(description="绘制矩形。参数: corner1, corner2, layer?, color?, lineweight?")
def draw_rectangle(
    corner1: List[float],
    corner2: List[float],
    layer: Optional[str] = None,
    color: Optional[int] = None,
    lineweight: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    result = cad.draw_rectangle(_as_point(corner1), _as_point(corner2), layer, color, lineweight)
    return {"ok": result is not None}


@mcp.tool(description="绘制多段线。参数: points, closed?, layer?, color?, lineweight?")
def draw_polyline(
    points: List[List[float]],
    closed: bool = False,
    layer: Optional[str] = None,
    color: Optional[int] = None,
    lineweight: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    pts = [_as_point(p) for p in points]
    result = cad.draw_polyline(pts, closed, layer, color, lineweight)
    return {"ok": result is not None}


@mcp.tool(description="添加文本。参数: position, text, height?, rotation?, layer?, color?")
def draw_text(
    position: List[float],
    text: str,
    height: float = 2.5,
    rotation: float = 0.0,
    layer: Optional[str] = None,
    color: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    result = cad.draw_text(_as_point(position), text, float(height), float(rotation), layer, color)
    return {"ok": result is not None}


@mcp.tool(description="绘制填充图案。参数: points, pattern_name?, scale?, layer?, color?")
def draw_hatch(
    points: List[List[float]],
    pattern_name: str = "SOLID",
    scale: float = 1.0,
    layer: Optional[str] = None,
    color: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    pts = [_as_point(p) for p in points]
    result = cad.draw_hatch(pts, pattern_name, float(scale), layer, color)
    return {"ok": result is not None}


@mcp.tool(description="添加线性标注。参数: start_point, end_point, text_position?, textheight?, layer?, color?")
def add_dimension(
    start_point: List[float],
    end_point: List[float],
    text_position: Optional[List[float]] = None,
    textheight: float = 5.0,
    layer: Optional[str] = None,
    color: Optional[int] = None,
) -> Dict[str, Any]:
    cad = _get_cad()
    text_pos = _as_point(text_position) if text_position else None
    result = cad.add_dimension(_as_point(start_point), _as_point(end_point), text_pos, float(textheight), layer, color)
    return {"ok": result is not None}


@mcp.tool(description="保存图纸。参数: file_path?（可为空，使用默认输出路径）")
def save_drawing(file_path: Optional[str] = None) -> Dict[str, Any]:
    cad = _get_cad()
    ok = cad.save_drawing(file_path)
    return {"ok": ok, "file_path": file_path}


@mcp.tool(description="创建图层。参数: layer_name, color?")
def create_layer(layer_name: str, color: int = 7) -> Dict[str, Any]:
    cad = _get_cad()
    ok = cad.create_layer(layer_name, color)
    return {"ok": ok}


@mcp.tool(description="处理结构化命令。参数: {action, params}")
def process_command(command: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """简单命令处理器。

    支持结构化命令：
    {"action": "draw_line", "params": {...}}
    """
    cad = _get_cad()

    if isinstance(command, dict):
        action = command.get("action")
        params = command.get("params", {})
        if not action:
            return {"ok": False, "error": "missing action"}

        if not hasattr(cad, action):
            return {"ok": False, "error": f"unsupported action: {action}"}

        func = getattr(cad, action)
        try:
            result = func(**params)
            return {"ok": result is not None}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    return {
        "ok": False,
        "error": "自然语言解析未启用，请使用结构化命令 {action, params}"
    }


if __name__ == "__main__":
    mcp.run("stdio")
