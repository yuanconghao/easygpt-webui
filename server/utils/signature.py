import hashlib
import hmac
import base64
from urllib.parse import quote


def generate_signature(appkey, accesstoken, timestamp, requestid=None):
    """
    生成请求的签名。

    :param appkey: 应用的appkey
    :param accesstoken: 用于签名的accesstoken
    :param timestamp: 请求的时间戳
    :param requestid: 请求的唯一ID（如果需要）
    :return: 已编码的签名字符串
    """
    # 准备签名原文
    params = {
        'appkey': appkey,
        'timestamp': timestamp
    }
    # 如果需要requestid，则添加到参数中
    if requestid:
        params['requestid'] = requestid

    # 对参数按字典序排序并拼接
    sorted_params_string = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
    print(sorted_params_string)

    # 使用accesstoken进行HmacSha256加密，然后进行base64编码
    signature_raw = hmac.new(accesstoken.encode(), sorted_params_string.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(signature_raw).decode()

    # 对signature进行urlencode
    signature_encoded = quote(signature)

    return signature_encoded
