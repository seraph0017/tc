"""Test Tencent Cloud VOD AIGC image generation with GPT Image 2 (ModelName=OG)."""
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

PROMPT = "一只在樱花树下打坐的橘色小猫，水彩风格，柔和光线，高细节"


def make_client() -> vod_client.VodClient:
    cred = credential.Credential(SECRET_ID, SECRET_KEY)
    http = HttpProfile()
    http.endpoint = ENDPOINT
    cp = ClientProfile()
    cp.httpProfile = http
    return vod_client.VodClient(cred, REGION, cp)


def submit(client: vod_client.VodClient) -> str:
    req = models.CreateAigcImageTaskRequest()
    body = {
        "SubAppId": SUB_APP_ID,
        "ModelName": "OG",
        "ModelVersion": "image2_medium",
        "Prompt": PROMPT,
        "OutputConfig": {
            "StorageMode": "Temporary",
            "AspectRatio": "1:1",
        },
        "ExtInfo": json.dumps({"AdditionalParameters": json.dumps({"resolution": "1K"})}),
    }
    req.from_json_string(json.dumps(body))
    resp = client.CreateAigcImageTask(req)
    print("submit response:", resp.to_json_string())
    return json.loads(resp.to_json_string())["TaskId"]


def poll(client: vod_client.VodClient, task_id: str, timeout: int = 300) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = models.DescribeTaskDetailRequest()
        req.from_json_string(json.dumps({"SubAppId": SUB_APP_ID, "TaskId": task_id}))
        resp = json.loads(client.DescribeTaskDetail(req).to_json_string())
        status = resp.get("Status")
        print(f"[{int(time.time()) % 1000}] status={status}")
        if status == "FINISH":
            return resp
        if status == "ERROR":
            raise RuntimeError(f"task failed: {json.dumps(resp, ensure_ascii=False)}")
        time.sleep(5)
    raise TimeoutError(f"task {task_id} did not finish in {timeout}s")


def main() -> None:
    client = make_client()
    task_id = submit(client)
    print(f"\ntask_id = {task_id}\n")
    result = poll(client, task_id)
    print("\nfinal:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # try to extract output URL and download
    aigc = result.get("AigcImageTask") or {}
    output = aigc.get("Output") or {}
    files = output.get("FileInfos") or output.get("FileInfoSet") or output.get("Files") or []
    for i, f in enumerate(files):
        url = f.get("FileUrl") or f.get("Url")
        if url:
            out = f"/tmp/gpt_image2_{i}.png"
            urllib.request.urlretrieve(url, out)
            print(f"saved -> {out}")


if __name__ == "__main__":
    main()
