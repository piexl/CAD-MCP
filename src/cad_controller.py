import logging
import math
import os
import json
from typing import Any, Dict, List, Optional, Tuple, Union
import sys

# 直接读取config.json文件
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 跨平台导入 - macOS/Linux 使用 ezdxf，Windows 可选 win32com
try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False
    logging.warning("未找到ezdxf库，将尝试使用win32com")

# 在 Windows 上尝试导入 win32com
try:
    import win32com.client
    import pythoncom
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

logger = logging.getLogger('cad_controller')

class CADController:
    """CAD 控制器类 - 支持 Windows (win32com) 和 macOS/Linux (ezdxf)"""
    
    def __init__(self):
        """初始化 CAD 控制器"""
        self.app = None
        self.doc = None
        self.entities = {}  # 存储已创建图形的实体引用
        
        # 从配置文件加载参数
        self.startup_wait_time = config["cad"].get("startup_wait_time", 20)
        self.command_delay = config["cad"].get("command_delay", 0.5)
        self.cad_type = config["cad"].get("type", "ezdxf")
        
        # 输出目录配置
        self.output_dir = config["output"].get("directory", "./output")
        self.default_filename = config["output"].get("default_filename", "cad_drawing.dwg")
        
        # 有效的线宽值列表
        self.valid_lineweights = [0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120, 140, 158, 200, 211]
        
        # 颜色映射 (DXF 颜色索引)
        self.color_map = {
            0: 0,      # 黑色
            1: 1,      # 红色
            2: 2,      # 黄色
            3: 3,      # 绿色
            4: 4,      # 青色
            5: 5,      # 蓝色
            6: 6,      # 洋红色
            7: 7,      # 白色
            256: 256   # 按图层设置
        }
        
        # 确定使用的后端
        self.use_ezdxf = False
        if HAS_EZDXF:
            self.use_ezdxf = True
            logger.info("使用 ezdxf 后端（跨平台支持）")
        elif HAS_WIN32COM and sys.platform == "win32":
            self.use_ezdxf = False
            logger.info("使用 win32com 后端（Windows COM 接口）")
        else:
            raise RuntimeError("未安装必要的 CAD 库。请安装 ezdxf 或在 Windows 上安装 pywin32")
        
        logger.info("CAD 控制器已初始化")
    
    def start_cad(self) -> bool:
        """启动 CAD 或创建新的 DXF 文档"""
        try:
            if self.use_ezdxf:
                return self._start_cad_ezdxf()
            else:
                return self._start_cad_win32com()
        except Exception as e:
            logger.error(f"启动 CAD 失败: {str(e)}")
            return False
    
    def _start_cad_ezdxf(self) -> bool:
        """使用 ezdxf 创建新的 DXF 文档"""
        try:
            # 创建新的 DXF 文档 (R2010 格式，兼容性好)
            self.doc = ezdxf.new('R2010')
            self.app = {"type": "ezdxf", "version": ezdxf.__version__}
            
            logger.info(f"已创建新的 DXF 文档 (ezdxf v{ezdxf.__version__})")
            return True
        except Exception as e:
            logger.error(f"创建 DXF 文档失败: {str(e)}")
            return False
    
    def _start_cad_win32com(self) -> bool:
        """使用 win32com 连接到本地 CAD 应用程序"""
        try:
            import pythoncom
            pythoncom.CoInitialize()
            
            app_id = "AutoCAD.Application"
            app_name = "AutoCAD"
            
            # 根据配置选择 CAD 类型
            cad_lower = self.cad_type.lower()
            if cad_lower == "gcad" or cad_lower == "gstarcad":
                app_id = "GCAD.Application"
                app_name = "GstarCAD"
            elif cad_lower == "zwcad":
                app_id = "ZWCAD.Application"
                app_name = "ZWCAD"
            
            # 尝试连接到已运行的实例
            try:
                self.app = win32com.client.GetActiveObject(app_id)
                logger.info(f"已连接到运行中的 {app_name} 实例")
            except:
                # 启动新实例
                logger.info(f"正在启动 {app_name} 实例...")
                self.app = win32com.client.Dispatch(app_id)
                self.app.Visible = True
                import time
                time.sleep(self.startup_wait_time)
            
            # 获取或创建文档
            if self.app.Documents.Count == 0:
                self.doc = self.app.Documents.Add()
            else:
                self.doc = self.app.ActiveDocument
            
            logger.info("CAD 已启动并准备就绪")
            return True
        except Exception as e:
            logger.error(f"Win32COM 启动失败: {str(e)}")
            return False
    
    def is_running(self) -> bool:
        """检查 CAD 是否正在运行"""
        return self.app is not None and self.doc is not None
    
    def save_drawing(self, file_path: str = None) -> bool:
        """保存当前图纸"""
        if not self.is_running():
            logger.error("CAD 未运行，无法保存图纸")
            return False
        
        try:
            if file_path is None:
                # 使用默认输出路径
                os.makedirs(self.output_dir, exist_ok=True)
                file_path = os.path.join(self.output_dir, self.default_filename)
            else:
                # 创建目录
                os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            
            if self.use_ezdxf:
                # ezdxf 保存
                self.doc.saveas(file_path)
            else:
                # win32com 保存
                self.doc.SaveAs(file_path)
            
            logger.info(f"图纸已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存图纸失败: {str(e)}")
            return False
    
    def create_layer(self, layer_name: str, color: int = 7) -> bool:
        """创建新图层"""
        if not self.is_running():
            return False
        
        try:
            if self.use_ezdxf:
                # ezdxf 创建图层
                if layer_name not in self.doc.layers:
                    self.doc.layers.new(name=layer_name, dxfattribs={'color': color})
                return True
            else:
                # win32com 创建图层
                for i in range(self.doc.Layers.Count):
                    if self.doc.Layers.Item(i).Name == layer_name:
                        self.doc.ActiveLayer = self.doc.Layers.Item(i)
                        return True
                
                new_layer = self.doc.Layers.Add(layer_name)
                self.doc.ActiveLayer = new_layer
                return True
        except Exception as e:
            logger.error(f"创建图层失败: {str(e)}")
            return False
    
    def draw_line(self, start_point: Tuple[float, float, float],
                  end_point: Tuple[float, float, float], 
                  layer: str = None, color: int = None, lineweight: int = None) -> Any:
        """绘制直线"""
        if not self.is_running():
            return None
        
        try:
            # 规范化点数据
            start_point = self._normalize_point(start_point)
            end_point = self._normalize_point(end_point)
            
            if self.use_ezdxf:
                # ezdxf 绘制直线
                dxfattribs = self._get_dxfattribs(layer, color, lineweight)
                line = self.doc.modelspace().add_line(start_point, end_point, dxfattribs=dxfattribs)
                return line
            else:
                # win32com 绘制直线
                import win32com.client
                import pythoncom
                start_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                       [start_point[0], start_point[1], start_point[2]])
                end_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                     [end_point[0], end_point[1], end_point[2]])
                
                line = self.doc.ModelSpace.AddLine(start_array, end_array)
                
                if layer:
                    self.create_layer(layer)
                    line.Layer = layer
                if color is not None:
                    line.Color = color
                if lineweight is not None:
                    line.LineWeight = self.validate_lineweight(lineweight)
                
                return line
        except Exception as e:
            logger.error(f"绘制直线失败: {str(e)}")
            return None
    
    def draw_circle(self, center: Tuple[float, float, float], radius: float,
                    layer: str = None, color: int = None, lineweight: int = None) -> Any:
        """绘制圆"""
        if not self.is_running():
            return None
        
        try:
            center = self._normalize_point(center)
            
            if self.use_ezdxf:
                dxfattribs = self._get_dxfattribs(layer, color, lineweight)
                circle = self.doc.modelspace().add_circle(center, radius, dxfattribs=dxfattribs)
                return circle
            else:
                import win32com.client
                import pythoncom
                center_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                        [center[0], center[1], center[2]])
                circle = self.doc.ModelSpace.AddCircle(center_array, radius)
                
                if layer:
                    self.create_layer(layer)
                    circle.Layer = layer
                if color is not None:
                    circle.Color = color
                
                return circle
        except Exception as e:
            logger.error(f"绘制圆失败: {str(e)}")
            return None
    
    def draw_arc(self, center: Tuple[float, float, float], radius: float,
                 start_angle: float, end_angle: float,
                 layer: str = None, color: int = None, lineweight: int = None) -> Any:
        """绘制圆弧"""
        if not self.is_running():
            return None
        
        try:
            center = self._normalize_point(center)
            
            if self.use_ezdxf:
                dxfattribs = self._get_dxfattribs(layer, color, lineweight)
                # ezdxf 使用度数表示角度
                arc = self.doc.modelspace().add_arc(center, radius, start_angle, end_angle, dxfattribs=dxfattribs)
                return arc
            else:
                import win32com.client
                import pythoncom
                center_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                        [center[0], center[1], center[2]])
                start_rad = math.radians(start_angle)
                end_rad = math.radians(end_angle)
                arc = self.doc.ModelSpace.AddArc(center_array, radius, start_rad, end_rad)
                
                if layer:
                    self.create_layer(layer)
                    arc.Layer = layer
                if color is not None:
                    arc.Color = color
                
                return arc
        except Exception as e:
            logger.error(f"绘制圆弧失败: {str(e)}")
            return None
    
    def draw_rectangle(self, corner1: Tuple[float, float, float],
                      corner2: Tuple[float, float, float],
                      layer: str = None, color: int = None, lineweight: int = None) -> Any:
        """绘制矩形"""
        if not self.is_running():
            return None
        
        try:
            corner1 = self._normalize_point(corner1)
            corner2 = self._normalize_point(corner2)
            
            # 计算矩形四个角
            x1, y1, z = corner1[0], corner1[1], corner1[2]
            x2, y2, _ = corner2[0], corner2[1], corner2[2]
            
            points = [
                (x1, y1, z),
                (x2, y1, z),
                (x2, y2, z),
                (x1, y2, z)
            ]
            
            return self.draw_polyline(points, closed=True, layer=layer, color=color, lineweight=lineweight)
        except Exception as e:
            logger.error(f"绘制矩形失败: {str(e)}")
            return None
    
    def draw_polyline(self, points: List[Tuple[float, float, float]], closed: bool = False,
                      layer: str = None, color: int = None, lineweight: int = None) -> Any:
        """绘制多段线"""
        if not self.is_running():
            return None
        
        try:
            if not points or len(points) < 2:
                logger.error("多段线至少需要 2 个点")
                return None
            
            points = [self._normalize_point(p) for p in points]
            
            if self.use_ezdxf:
                dxfattribs = self._get_dxfattribs(layer, color, lineweight)
                pline = self.doc.modelspace().add_lwpolyline(points, dxfattribs=dxfattribs)
                if closed:
                    pline.close()
                return pline
            else:
                import win32com.client
                import pythoncom
                point_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                       [coord for p in points for coord in p])
                pline = self.doc.ModelSpace.AddPolyline(point_array)
                
                if closed and len(points) > 2:
                    pline.Closed = True
                
                if layer:
                    self.create_layer(layer)
                    pline.Layer = layer
                if color is not None:
                    pline.Color = color
                
                return pline
        except Exception as e:
            logger.error(f"绘制多段线失败: {str(e)}")
            return None
    
    def draw_text(self, position: Tuple[float, float, float], text: str,
                  height: float = 2.5, rotation: float = 0,
                  layer: str = None, color: int = None) -> Any:
        """添加文本"""
        if not self.is_running():
            return None
        
        try:
            position = self._normalize_point(position)
            
            if self.use_ezdxf:
                dxfattribs = self._get_dxfattribs(layer, color, None)
                dxfattribs['height'] = height
                dxfattribs['rotation'] = rotation
                text_obj = self.doc.modelspace().add_text(text, dxfattribs=dxfattribs)
                text_obj.set_placement(position, align=0)  # 左下对齐
                return text_obj
            else:
                import win32com.client
                import pythoncom
                position_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                          [position[0], position[1], position[2]])
                text_obj = self.doc.ModelSpace.AddText(text, position_array, height)
                
                if rotation != 0:
                    text_obj.Rotation = math.radians(rotation)
                
                if layer:
                    self.create_layer(layer)
                    text_obj.Layer = layer
                if color is not None:
                    text_obj.Color = color
                
                return text_obj
        except Exception as e:
            logger.error(f"添加文本失败: {str(e)}")
            return None
    
    def draw_hatch(self, points: List[Tuple[float, float, float]], pattern_name: str = "SOLID",
                   scale: float = 1.0, layer: str = None, color: int = None) -> Any:
        """绘制填充图案"""
        if not self.is_running() or not points or len(points) < 3:
            return None
        
        try:
            points = [self._normalize_point(p)[:2] for p in points]  # 转为 2D
            
            if self.use_ezdxf:
                dxfattribs = self._get_dxfattribs(layer, color, None)
                dxfattribs['pattern'] = pattern_name
                dxfattribs['scale'] = scale
                
                # 创建多段线作为边界
                hatch = self.doc.modelspace().add_hatch(dxfattribs=dxfattribs)
                
                # 添加外边界
                pline = self.doc.modelspace().add_lwpolyline(points)
                pline.close()
                hatch.append_polyline_path(pline)
                
                return hatch
            else:
                # win32com 填充逻辑
                pline = self.draw_polyline(points, closed=True, layer=layer)
                if not pline:
                    return None
                
                import win32com.client
                import pythoncom
                hatch = self.doc.ModelSpace.AddHatch(0, pattern_name, True)
                object_ids = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [pline])
                hatch.AppendOuterLoop(object_ids)
                hatch.PatternScale = scale
                hatch.Evaluate()
                
                if layer:
                    self.create_layer(layer)
                    hatch.Layer = layer
                if color is not None:
                    hatch.Color = color
                
                return hatch
        except Exception as e:
            logger.error(f"绘制填充失败: {str(e)}")
            return None
    
    def add_dimension(self, start_point: Tuple[float, float, float],
                      end_point: Tuple[float, float, float],
                      text_position: Tuple[float, float, float] = None,
                      textheight: float = 5, layer: str = None, color: int = None) -> Any:
        """添加线性标注"""
        if not self.is_running():
            return None
        
        try:
            start_point = self._normalize_point(start_point)
            end_point = self._normalize_point(end_point)
            
            if text_position is None:
                # 自动计算文本位置
                mid_x = (start_point[0] + end_point[0]) / 2
                mid_y = (start_point[1] + end_point[1]) / 2
                text_position = (mid_x, mid_y + 5, 0)
            else:
                text_position = self._normalize_point(text_position)
            
            if self.use_ezdxf:
                dxfattribs = self._get_dxfattribs(layer, color, None)
                dxfattribs['text_height'] = textheight
                
                # ezdxf 线性标注
                dim = self.doc.modelspace().add_linear_dimension_2p(
                    start_point, end_point, text_position, dxfattribs=dxfattribs
                )
                return dim
            else:
                import win32com.client
                import pythoncom
                start_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                       [start_point[0], start_point[1], start_point[2]])
                end_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                     [end_point[0], end_point[1], end_point[2]])
                text_pos_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,
                                                          [text_position[0], text_position[1], text_position[2]])
                
                dimension = self.doc.ModelSpace.AddDimAligned(start_array, end_array, text_pos_array)
                
                if textheight:
                    dimension.TextHeight = textheight
                if layer:
                    self.create_layer(layer)
                    dimension.Layer = layer
                if color is not None:
                    dimension.Color = color
                
                return dimension
        except Exception as e:
            logger.error(f"添加标注失败: {str(e)}")
            return None
    
    def validate_lineweight(self, lineweight: int) -> int:
        """验证线宽"""
        if lineweight is None or lineweight in self.valid_lineweights:
            return lineweight
        logger.warning(f"线宽值 {lineweight} 无效，使用默认值 0")
        return 0
    
    def refresh_view(self) -> None:
        """刷新视图 (仅 Windows COM)"""
        if not self.use_ezdxf and self.is_running():
            try:
                self.doc.Regen(1)
            except:
                pass
    
    def close(self) -> None:
        """关闭 CAD 连接"""
        try:
            if not self.use_ezdxf and HAS_WIN32COM:
                import pythoncom
                if self.app:
                    del self.app
                pythoncom.CoUninitialize()
        except:
            pass
    
    # ==================== 辅助方法 ====================
    
    def _normalize_point(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """规范化点为三维坐标"""
        if len(point) == 2:
            return (point[0], point[1], 0)
        return tuple(point[:3])
    
    def _get_dxfattribs(self, layer: str = None, color: int = None, lineweight: int = None) -> Dict[str, Any]:
        """获取 DXF 属性字典"""
        dxfattribs = {}
        
        if layer:
            self.create_layer(layer)
            dxfattribs['layer'] = layer
        
        if color is not None:
            dxfattribs['color'] = color
        
        if lineweight is not None:
            lineweight = self.validate_lineweight(lineweight)
            if lineweight is not None:
                dxfattribs['lineweight'] = lineweight
        
        return dxfattribs
