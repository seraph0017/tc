"""Generate cover + closing images for Lesson 01 via Tencent VOD GPT Image 2."""
import json
import os
import time
import urllib.request

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.vod.v20180717 import models, vod_client

SECRET_ID = os.environ["TENCENTCLOUD_SECRET_ID"]
SECRET_KEY = os.environ["TENCENTCLOUD_SECRET_KEY"]
REGION = os.environ.get("TENCENTCLOUD_REGION", "ap-nanjing")
SUB_APP_ID = int(os.environ["TENCENTCLOUD_VOD_SUB_APP_ID"])
ENDPOINT = os.environ.get("TENCENTCLOUD_VOD_ENDPOINT", "vod.tencentcloudapi.com")

ASSETS = "/Users/nathan/Projects/tc/01-ai-agent-engineering/ppt/assets"
os.makedirs(ASSETS, exist_ok=True)

JOBS = [
    {
        "name": "cover",
        "prompt": (
            "一颗发光的人脑与精密的齿轮、神经突触和数据流光线相互交融，"
            "象征AI的记忆觉醒，深蓝色科技背景，配以橙色光点，水彩与扁平插画混合风格，"
            "高细节，柔和发光，无文字"
        ),
        "ratio": "16:9",
    },
    {
        "name": "closing",
        "prompt": (
            "多层透明书架与发光的神经网络交织在一起，从底部到顶部分为四层，"
            "象征记忆的层级架构，深蓝色背景配橙色高光，扁平插画风，柔和光线，"
            "高质感，无文字"
        ),
        "ratio": "16:9",
    },
]


def make_client():
    cred = credential.Credential(SECRET_ID, SECRET_KEY)
    http = HttpProfile()
    http.endpoint = ENDPOINT
    cp = ClientProfile()
    cp.httpProfile = http
    return vod_client.VodClient(cred, REGION, cp)


def submit(client, prompt, ratio):
    req = models.CreateAigcImageTaskRequest()
    body = {
        "SubAppId": SUB_APP_ID,
        "ModelName": "OG",
        "ModelVersion": "image2_medium",
        "Prompt": prompt,
        "OutputConfig": {"StorageMode": "Temporary", "AspectRatio": ratio},
        "ExtInfo": json.dumps({"AdditionalParameters": json.dumps({"resolution": "1K"})}),
    }
    req.from_json_string(json.dumps(body))
    resp = client.CreateAigcImageTask(req)
    return json.loads(resp.to_json_string())["TaskId"]


def poll(client, task_id, timeout=400):
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = models.DescribeTaskDetailRequest()
        req.from_json_string(json.dumps({"SubAppId": SUB_APP_ID, "TaskId": task_id}))
        resp = json.loads(client.DescribeTaskDetail(req).to_json_string())
        status = resp.get("Status")
        if status == "FINISH":
            return resp
        if status == "ERROR":
            raise RuntimeError(json.dumps(resp, ensure_ascii=False))
        time.sleep(5)
    raise TimeoutError(task_id)


def main():
    client = make_client()
    results = {}
    for job in JOBS:
        print(f"[submit] {job['name']}")
        tid = submit(client, job["prompt"], job["ratio"])
        print(f"  task_id={tid}")
        result = poll(client, tid)
        files = (result.get("AigcImageTask") or {}).get("Output", {}).get("FileInfos") or []
        if not files:
            print(f"  no output! raw={json.dumps(result, ensure_ascii=False)[:300]}")
            continue
        url = files[0].get("FileUrl") or files[0].get("Url")
        out = os.path.join(ASSETS, f"{job['name']}.png")
        urllib.request.urlretrieve(url, out)
        print(f"  saved -> {out}")
        results[job["name"]] = out
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
