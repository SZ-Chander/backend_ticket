from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
from ticket_ocr_service import TicketOCRService
import base64
from tools import Tools
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Railway Ticket Recognition API",
    description="车票识别 / 健康检查 / 预留扩展",
    version="0.2.0"
)

stations_dictionary = Tools.read_json("{}/setting/translate_dict.json".format(BASE_DIR))
guidance_jp = Tools.read_json("{}/setting/guidance_jp.json".format(BASE_DIR))
guidance_en = Tools.read_json("{}/setting/guidance_en.json".format(BASE_DIR))
guidance_cn = Tools.read_json("{}/setting/guidance_cn.json".format(BASE_DIR))
guidance_tw = Tools.read_json("{}/setting/guidance_tw.json".format(BASE_DIR))
guidance_hk = Tools.read_json("{}/setting/guidance_hk.json".format(BASE_DIR))
guidance_ko = Tools.read_json("{}/setting/guidance_ko.json".format(BASE_DIR))
guidance_es = Tools.read_json("{}/setting/guidance_sp.json".format(BASE_DIR))
# guidance_es = Tools.read_json("/Users/szchandler/Desktop/localCode/Ticket_OCR/Backend_Ticket_JR/setting/guidance_sp.json")


guidanceBooks = {"jp": guidance_jp, "en": guidance_en,"cn": guidance_cn,"tw": guidance_tw,"hk": guidance_hk,"ko": guidance_ko,"es": guidance_es}
# 1. 主方法 —— 车票识别接口（支持多图片 + 参数）
@app.post("/recognize-ticket")
async def recognize_ticket(
    files: List[UploadFile] = File(..., description="一张或多张车票图片"),
    language = Form(...,description="语言设置"),
    location: str = Form(..., description="使用者位置，不能为空"),
    ticket_type: str = Form(..., description="车票类型，不能为空"),
    departure: Optional[str] = Form(None, description="出发站，可为空"),
    arrival: Optional[str] = Form(None, description="终到站，可为空"),
):
    """
    上传车票图片 + 参数
    - files: 一张或多张图片
    - location: 使用者位置（必填）
    - departure: 出发站（选填）
    - arrival: 终到站（选填）
    """
    img_b64_list = []

    for f in files:
        # 异步读取文件内容（不落地）
        raw_bytes = await f.read()

        # 转 base64 字符串
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        img_b64_list.append(b64_str)
    ticket_ocr_service = TicketOCRService()
    ticket_data = ticket_ocr_service.ticket_ocr_service(img_b64_list,language,stations_dictionary,location=location,ticket_type=ticket_type,guidanceBooks=guidanceBooks)



    file_info = [{"filename": f.filename, "content_type": f.content_type} for f in files]

    # gpt调用主方法逻辑

    # 主方法逻辑结束

    # return {
    #     "status": "received",
    #     "location": location,
    #     "departure": departure,
    #     "arrival": arrival,
    #     "files": file_info
    # }
    return {
        "status": "ok",
        "ticket_data" : ticket_data
    }


# 2. 测试方法 —— 健康检查
@app.get("/ping")
async def ping():
    return {"message": "pong"}


# 3. 空方法 —— 预留扩展
@app.get("/future-feature")
async def future_feature():
    return {"message": "future feature not implemented yet"}


# 本地调试入口
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
