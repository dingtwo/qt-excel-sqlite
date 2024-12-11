import hashlib
import requests
from datetime import datetime
import re
import random
import time

# MD5加密函数


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def do_access_token():
    username = "永辉彩食鲜VOP"
    pass_word = "csxBJ2024·qygyh"
    client_id = "nkJAqxsySFtJL3FmFqRy"
    client_secret = "RIsFDwXauZeYVomqO4gf"

    # 固定值 access_token
    grant_type = "access_token"

    # 当前时间 格式yyyy-MM-dd HH:mm:ss
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 密码进行MD5加密
    password_md5 = md5(pass_word)

    # 构建请求参数
    params = {
        "grant_type": grant_type,
        "username": username,
        "password": password_md5,
        "timestamp": timestamp,
        "client_id": client_id,
    }

    # 认证标识的计算
    sign_str = (
        client_secret
        + timestamp
        + client_id
        + username
        + password_md5
        + grant_type
        + client_secret
    )
    params["sign"] = md5(sign_str).upper()

    # 执行请求
    url = "https://bizapi.jd.com/oauth2/accessToken"  # 请根据实际情况修改url
    response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()  # 假设返回的是JSON格式
        return result
    else:
        print("请求失败:", response.status_code, response.text)
        return None


# 调用函数
# result = do_access_token()
# if result:
#     print(result)

# sys.exit(0)


def extract_number(url):
    if isinstance(url, str):
        match = re.search(r"(\d+)\.html", url)
        if match:
            return match.group(1)
    return None


# 从 resultMessage 中提取错误信息
def get_error_message(result_message, sku_id):
    # 处理 resultMessage 查找对应 SKU 的错误信息
    sku_id_str = str(sku_id)
    if sku_id_str in result_message:
        # 提取该 SKU 的错误信息（假设每个 SKU 错误信息都是以 "skuId 错误信息" 的形式）
        start_index = result_message.find(sku_id_str) + len(sku_id_str)
        end_index = result_message.find("。", start_index) + 1
        return result_message[start_index:end_index]
    return None


# 批量请求接口获取价格的函数
def fetch_prices(sku_ids):
    sleep_time = random.uniform(0, 3.5)  # 随机生成一个 0.5 到 1.5 秒的延迟时间
    time.sleep(sleep_time)
    url = "https://bizapi.jd.com/api/price/getSellPrice"  # 替换为实际的接口 URL
    params = {
        "sku": ",".join(sku_ids),
        "token": "DnweEZ0PJRhEGTKRSETAAykDu",
        "queryExts": "price,marketPrice",
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json()  # 假设返回的是 JSON 格式的数据
    else:
        print(f"请求失败: {response.status_code}")
        return []


def batch_fetch_prices(sku_ids):
    result = {}
    prices = fetch_prices(sku_ids)
    print(prices)
    # 使用 skuId 匹配价格数据，并将 jdPrice 写回 DataFrame
    sku_to_price = {str(price["skuId"]): price["jdPrice"] for price in prices["result"]}
    result_message = prices.get(
        "resultMessage", ""
    )  # 获取结果消息，假设所有商品的 resultMessage 是一样的
    index = 0
    for sku_id in sku_ids:
        sku_id_str = str(sku_id)
        if sku_id_str in sku_to_price:
            result[index] = {"price": sku_to_price[sku_id_str], "status": "success"}
        else:
            # 从resultMessage中获取原因
            error_message = get_error_message(result_message, sku_id)
            if error_message:
                result[index] = {
                    "price": "",
                    "status": "error",
                    "error_message": error_message,
                }
            else:
                result[index] = {
                    "price": "",
                    "status": "error",
                    "error_message": "未知错误",
                }
        index += 1
    return result


# res = batch_fetch_prices(['100044464662'])
# print(res)


def fetch_price_from_wanbang(sku_id):
    # sleep_time = random.uniform(0, 3.5)  # 随机生成一个 0.5 到 1.5 秒的延迟时间
    # time.sleep(sleep_time)
    url = "https://api-gw.onebound.cn/jd/item_sku"  # 替换为实际的接口 URL
    params = {
        "sku_id": sku_id,
        "key": "t3998684950",
        "cache": "no",
        "lang": "zh-CN",
        "secret": "20240927",
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        res = response.json()  # 假设返回的是 JSON 格式的数据
        if res["error"] == "" and res["item"]:
            res_sku_id = res["item"]["sku_id"]
            if res_sku_id != sku_id:
                error_message = (
                    f"返回的和请求的不一致：入参{sku_id}，返回：{res_sku_id}"
                )
                print(error_message)
                return {"price": "", "status": "error", "error_message": error_message}
            else:
                return {
                    "price": res["item"]["price"],
                    "status": "success",
                }
        else:
            error_message = f"异常：入参{sku_id}，原因：{res['reason']}"
            if "item-not-found" in res["reason"]:
                return {
                    "price": "失效",
                    "status": "success",
                }
            return {
                "price": "",
                "error_message": error_message,
                "status": "error",
            }
    else:
        print(f"请求失败: {response.status_code}")
        return {
            "price": "",
            "name": f"状态码:${response.status_code},内容：{response.text}",
            "status": "error",
        }


# res = fetch_price_from_wanbang("100044464662")
# print(res)
