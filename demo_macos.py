#!/usr/bin/env python
"""
macOS CAD-MCP 快速演示脚本
展示如何使用适配后的 CAD 控制器
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cad_controller import CADController
from nlp_processor import NLPProcessor

def demo_basic_drawing():
    """演示基础绘图功能"""
    print("\n" + "="*60)
    print("🎨 CAD-MCP macOS 演示 - 基础绘图")
    print("="*60)
    
    # 初始化控制器
    cad = CADController()
    
    print("\n1️⃣  启动 CAD (创建新的 DXF 文档)...")
    if not cad.start_cad():
        print("❌ 启动失败")
        return
    
    print("✅ CAD 已启动")
    print(f"   后端: {'ezdxf (跨平台)' if cad.use_ezdxf else 'Win32COM (Windows)'}")
    
    # 创建图层
    print("\n2️⃣  创建图层...")
    cad.create_layer("geometry", color=1)
    cad.create_layer("lines", color=3)
    cad.create_layer("text", color=5)
    print("✅ 已创建 3 个图层")
    
    # 绘制基本形状
    print("\n3️⃣  绘制形状...")
    
    # 圆形
    circle = cad.draw_circle((0, 0, 0), 10, layer="geometry", color=1)
    print(f"   ✓ 圆 (半径=10)")
    
    # 直线
    line = cad.draw_line((0, 0, 0), (20, 20, 0), layer="lines", color=3)
    print(f"   ✓ 直线 (从 (0,0) 到 (20,20))")
    
    # 矩形
    rect = cad.draw_rectangle((5, 5, 0), (15, 15, 0), layer="geometry", color=5)
    print(f"   ✓ 矩形 (5,5)-(15,15)")
    
    # 文本
    text = cad.draw_text((0, -5, 0), "CAD-MCP on macOS!", height=3, layer="text", color=7)
    print(f"   ✓ 文本")
    
    # 多段线
    polyline = cad.draw_polyline([
        (-10, -10, 0),
        (-10, 10, 0),
        (10, 10, 0),
        (10, -10, 0)
    ], closed=True, layer="lines", color=4)
    print(f"   ✓ 多段线 (4 个点)")
    
    # 保存文件
    print("\n4️⃣  保存绘图...")
    output_file = "./output/demo_drawing.dwg"
    os.makedirs("./output", exist_ok=True)
    
    if cad.save_drawing(output_file):
        print(f"✅ 文件已保存: {output_file}")
    else:
        print(f"❌ 保存失败")
    
    cad.close()
    
    print("\n" + "="*60)
    print("✨ 演示完成！")
    print("="*60)
    print(f"\n📄 输出文件: {os.path.abspath(output_file)}")
    print("   你可以用任何支持 DWG 的软件打开这个文件")
    print("   推荐: LibreCAD (免费, 支持 macOS)")
    print("\n💡 下一步:")
    print("   1. 查看 src/nlp_processor.py 了解自然语言处理")
    print("   2. 查看 src/server.py 了解 MCP 集成")
    print("   3. 查看 MACOS_SETUP.md 了解完整配置")


def demo_nlp():
    """演示自然语言处理"""
    print("\n" + "="*60)
    print("🤖 自然语言处理演示")
    print("="*60)
    
    nlp = NLPProcessor()
    
    # 测试命令解析
    test_commands = [
        "在 (0,0) 到 (10,10) 绘制一条红色直线",
        "绘制一个半径为 5 的蓝色圆",
        "创建一个绿色矩形",
    ]
    
    print("\n测试命令:")
    for cmd in test_commands:
        print(f"  📝 '{cmd}'")
    
    print("\n✅ NLPProcessor 已初始化")
    print("   可以处理中文和英文命令")


if __name__ == "__main__":
    print("\n🚀 CAD-MCP macOS 快速演示\n")
    
    # 运行演示
    demo_basic_drawing()
    demo_nlp()
    
    print("\n📚 更多信息:\n")
    print("   • MACOS_SETUP.md - macOS 完整设置指南")
    print("   • README.md - 项目概述")
    print("   • src/server.py - MCP 服务器实现")
    print("\n✨ 完成!\n")
