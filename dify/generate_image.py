import os
import requests
import json

scenes = "[\n    {\n        \"no\": 1,\n        \"scene\": \"小猪在月宫的云朵上玩耍\",\n        \"describe\": {\n            \"镜头类型\": \"远景\",\n            \"摄像机角度\": \"俯拍\",\n            \"镜头运动\": \"缓慢的横向移动\",\n            \"画面构图\": \"小猪在画面中央，周围是漂浮的云朵和星星\",\n            \"灯光风格\": \"柔和的月光\",\n            \"色彩基调\": \"银蓝色调，点缀着金色的星光\"\n        }\n    },\n    {\n        \"no\": 2,\n        \"scene\": \"小猪发现了一颗坠落的星星\",\n        \"describe\": {\n            \"镜头类型\": \"中景\",\n            \"摄像机角度\": \"平视\",\n            \"镜头运动\": \"推近\",\n            \"画面构图\": \"小猪伸出蹄子，试图接住坠落的星星\",\n            \"灯光风格\": \"星星发出温暖的橙黄色光芒\",\n            \"色彩基调\": \"深蓝色背景，星星的光芒形成强烈的对比\"\n        }\n    },\n    {\n        \"no\": 3,\n        \"scene\": \"小猪和星星一起在银河中漂流\",\n        \"describe\": {\n            \"镜头类型\": \"远景\",\n            \"摄像机角度\": \"低角度\",\n            \"镜头运动\": \"跟随拍摄\",\n            \"画面构图\": \"小猪和星星在银河中漂流，周围是闪烁的星群\",\n            \"灯光风格\": \"银河的微光和星星的闪烁\",\n            \"色彩基调\": \"深紫色和蓝色，银河呈现银白色\"\n        }\n    },\n    {\n        \"no\": 4,\n        \"scene\": \"小猪将星星送回天空\",\n        \"describe\": {\n            \"镜头类型\": \"特写\",\n            \"摄像机角度\": \"仰拍\",\n            \"镜头运动\": \"固定\",\n            \"画面构图\": \"小猪用蹄子轻轻托起星星，星星缓缓升空\",\n            \"灯光风格\": \"星星的光芒逐渐增强\",\n            \"色彩基调\": \"深蓝色天空，星星的光芒照亮小猪的脸\"\n        }\n    },\n    {\n        \"no\": 5,\n        \"scene\": \"小猪在月宫中安睡\",\n        \"describe\": {\n            \"镜头类型\": \"中景\",\n            \"摄像机角度\": \"俯拍\",\n            \"镜头运动\": \"缓慢拉远\",\n            \"画面构图\": \"小猪蜷缩在云朵上，周围是宁静的夜空\",\n            \"灯光风格\": \"柔和的月光洒在小猪身上\",\n            \"色彩基调\": \"宁静的深蓝色，点缀着淡淡的银色月光\"\n        }\n    }\n]"

os.environ["ARK_API_KEY"] = "f67a41e6-d67a-408e-8126-fedc243a79fb"
def main(scenes: list) -> list:
    # 配置参数
    ARK_API_KEY = os.environ.get("ARK_API_KEY")  # 从环境变量获取API Key
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"  

    urls = []
    scenes = json.loads(scenes)
    for pic in scenes:
        scene_describe = str(pic)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ARK_API_KEY}"
        }

        payload = {
            "model": "doubao-seedream-3-0-t2i-250415",
            "prompt": scene_describe,
            "size": "1024x1024",
            "response_format": "url",
            "watermark": True
        }

        try:
            response = requests.post(
                BASE_URL,
                headers=headers,
                json=payload  # 直接使用json参数自动序列化
            )
            
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            
            # 提取URL（
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0]['url']
                urls.append(image_url)
                print(f"生成成功: {image_url}")
            else:
                print("响应中未找到有效的URL", result)

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            print(f"错误响应: {response.text if 'response' in locals() else '无响应'}")

    # 最终所有生成的URL
    print("所有生成的图片URL:", urls)

if __name__ == "__main__":
    main(scenes)