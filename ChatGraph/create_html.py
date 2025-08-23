import json

def main(arg: str) -> dict:
    data = arg.replace("```", "").replace("javascript", "")
    html = f"""
        <!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>节点关系图</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://unpkg.com/vis-network/styles/vis-network.min.css" rel="stylesheet" type="text/css" />
    <style>
        #network-container {{
            width: 100%;
            height: 100vh;
            border: 1px solid #ccc;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
        }}
        
        .tooltip {{
            position: absolute;
            background-color: rgba(255, 255, 255, 0.95);
            border: 1px solid #6c9eec;
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
            pointer-events: none;
            z-index: 1000;
            font-size: 14px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            backdrop-filter: blur(4px);
        }}
        
        /* 节点标签省略号样式 */
        .vis-label {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }}
    </style>
</head>
<body>
    <div id="network-container"></div>
    <div id="tooltip" class="tooltip" style="display: none;"></div>

    <script>
        // 预定义颜色数组
        const nodeColors = [
            {{background: '#FF6B6B', border: '#D32F2F', highlight: {{background: '#FF8A80', border: '#B71C1C'}}}},  // 红色系
            {{background: '#4ECDC4', border: '#009688', highlight: {{background: '#80E6DE', border: '#00796B'}}}},  // 青色系
            {{background: '#45B7D1', border: '#1976D2', highlight: {{background: '#81D4FA', border: '#0D47A1'}}}},  // 蓝色系
            {{background: '#FFBE0B', border: '#FF8F00', highlight: {{background: '#FFD54F', border: '#E65100'}}}},  // 黄色系
            {{background: '#9B5DE5', border: '#7B1FA2', highlight: {{background: '#CE93D8', border: '#4A148C'}}}},  // 紫色系
            {{background: '#00BB9D', border: '#00796B', highlight: {{background: '#4DB6AC', border: '#004D40'}}}},  // 绿色系
            {{background: '#F15BB5', border: '#C2185B', highlight: {{background: '#F48FB1', border: '#880E4F'}}}},  // 粉色系
            {{background: '#00BBF9', border: '#0288D1', highlight: {{background: '#81D4FA', border: '#01579B'}}}}   // 天蓝色系
        ];
        
        const edgeColors = [
            {{color: '#D32F2F', highlight: '#FFCDD2'}},  // 红色系
            {{color: '#009688', highlight: '#B2DFDB'}},  // 青色系
            {{color: '#1976D2', highlight: '#BBDEFB'}},  // 蓝色系
            {{color: '#FF8F00', highlight: '#FFE0B2'}},  // 黄色系
            {{color: '#7B1FA2', highlight: '#E1BEE7'}},  // 紫色系
            {{color: '#00796B', highlight: '#B2DFDB'}},  // 绿色系
            {{color: '#C2185B', highlight: '#F8BBD0'}},  // 粉色系
            {{color: '#0288D1', highlight: '#BBDEFB'}},  // 天蓝色系
            {{color: '#757575', highlight: '#E0E0E0'}}   // 灰色系
        ];

        // 随机选择颜色的函数
        function getRandomNodeColor(type) {{
            if (type === 'company') {{
                return {{background: '#45B7D1', border: '#619FBC', highlight: {{background: '#81D4FA', border: '#0D47A1'}}}};  // 蓝色系
            }}if (type === 'person') {{
                return {{background: '#FFA726', border: '#FF8F00', highlight: {{background: '#FFD54F', border: '#FF6F00'}}}};  // 黄色系
            }} else
                return {{background: '#FF1744', border: '#D50000', highlight: {{background: '#FF4081', border: '#C2185B'}}}};       
        }}
        
        function getRandomEdgeColor() {{
            return {{color: '#757575', highlight: '#E0E0E0'}};
        }}

        // 创建节点和边数据
        function truncateLabel(label, maxLength = 8) {{
            if (label.length > maxLength) {{
                return label.substring(0, maxLength) + '...';
            }}
            return label;
        }}
        
        {data}

        // 创建网络图
        const container = document.getElementById('network-container');
        const tooltip = document.getElementById('tooltip');
        const data = {{
            nodes: nodes,
            edges: edges
        }};
        const options = {{
            physics: {{
                enabled: true,
                stabilization: {{ iterations: 150 }},
                solver: 'repulsion',
                repulsion: {{
                    nodeDistance: 200,
                    centralGravity: 0.1,
                    springLength: 300,
                    springConstant: 0.05
                }}
            }},
            nodes: {{
                borderWidth: 3,
                font: {{ 
                    color: '#ffffff',
                    size: 24,
                    face: 'Segoe UI',
                    bold: {{
                        color: '#ffffff',
                        size: 22
                    }}
                }},
                shape: 'circle',
                size: 90,
                scaling: {{
                    label: {{
                        enabled: false
                    }}
                }},
                chosen: {{
                    node: function(values, id, selected, hovering) {{
                        values.shadow = true;
                        values.shadowColor = 'rgba(0,0,0,0.2)';
                        values.shadowSize = 15;
                        values.shadowX = 0;
                        values.shadowY = 0;
                    }}
                }},
                widthConstraint: {{
                    maximum: 170
                }},
                title: undefined  // 禁用节点默认title
            }},
            edges: {{
                font: {{ 
                    size: 16,
                    color: '#444',
                    background: 'rgba(255, 255, 255, 0.8)',
                    strokeWidth: 2,
                    strokeColor: '#ffffff'
                }},
                arrows: {{
                    to: {{enabled: true, scaleFactor: 1.2, type: 'arrow'}}
                }},
                smooth: {{
                    enabled: true,
                    type: "dynamic",
                    roundness: 0.5
                }},
                width: 3,
                chosen: {{
                    edge: function(values, id, selected, hovering) {{
                        values.shadow = true;
                        values.shadowColor = 'rgba(0,0,0,0.2)';
                        values.shadowSize = 10;
                        values.shadowX = 0;
                        values.shadowY = 0;
                    }}
                }},
                widthConstraint: {{
                    maximum: 150
                }},
                title: undefined  // 禁用边默认title
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100000  // 设置极大延迟，实际禁用默认tooltip
            }}
        }};
        
        const network = new vis.Network(container, data, options);
        
        // 禁用默认tooltip显示
        network.on("beforeDrawing", function (ctx) {{
            // 确保不显示默认的title tooltip
        }});
        
        // 添加鼠标悬停事件
        network.on("hoverNode", function (params) {{
            const nodeId = params.node;
            const node = nodes.find(n => n.id === nodeId);
            if (node && node.title) {{
                showTooltip(node.title, params.event);
            }}
        }});
        
        network.on("hoverEdge", function (params) {{
            const edgeId = params.edge;
            const edge = edges.find(e => 
                e.from === network.body.edges[edgeId].fromId && 
                e.to === network.body.edges[edgeId].toId
            );
            if (edge && edge.title) {{
                showTooltip(edge.title, params.event);
            }}
        }});
        
        network.on("blurNode", function (params) {{
            hideTooltip();
        }});
        
        network.on("blurEdge", function (params) {{
            hideTooltip();
        }});
        
        network.on("dragStart", function (params) {{
            hideTooltip();
        }});
        
        function showTooltip(text, event) {{
            // 解析JSON格式的title内容
            let displayText = text;
            try {{
                const jsonData = JSON.parse(text);
                displayText = '';
                for (const [key, value] of Object.entries(jsonData)) {{
                    displayText += `<strong>${{key}}:</strong> ${{value}}<br>`;
                }}
            }} catch (e) {{
                // 如果不是JSON格式，直接显示原文本
                displayText = text;
            }}
            
            tooltip.innerHTML = displayText;
            tooltip.style.display = 'block';
            tooltip.style.left = (event.clientX + 15) + 'px';
            tooltip.style.top = (event.clientY + 15) + 'px';
        }}
        
        function hideTooltip() {{
            tooltip.style.display = 'none';
        }}
        
        // 鼠标移动时更新tooltip位置
        container.addEventListener('mousemove', function(event) {{
            if (tooltip.style.display === 'block') {{
                tooltip.style.left = (event.clientX + 15) + 'px';
                tooltip.style.top = (event.clientY + 15) + 'px';
            }}
        }});
    </script>
</body>
</html>
    """
    return {
        "result": data
    }
