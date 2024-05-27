import json
import os
import time
import io
import requests
import websocket
import time
import uuid
import base64
from server.utils.signature import generate_signature
from flask import Flask, jsonify
from server.models.tts import TTSGenerator


class TXDHGenerator:

    @staticmethod
    def create_session(appkey, access_token, virtualmankey):

        # str1 = "{'Header': {'RequestID': 'bjed97692a17164350740778646', 'SessionID': 'bjed97692a17164350740778647', 'DialogID': '', 'Code': 0, 'Message': ''}, 'Payload': {'SessionId': 'm14272810838917134688', 'PlayStreamAddr': 'rtmp://liveplay.ivh.qq.com/live/m14272810838917134688', 'SessionStatus': 3, 'ReqId': '7ea66c1fc1e34f318f35055430066df7'}}"
        # # 使用正则表达式将单引号替换为双引号
        # str1 = str1.replace("'", '"')
        #
        # str1_dict = json.loads(str1)
        # print(str1_dict)
        # return jsonify(str1_dict)

        user_id = 'f2612aa810014e8997f95bda97917268'
        # protocol = 'webrtc'
        protocol = 'rtmp'
        driver_type = 3
        protocol_option = None  # 如果有额外的ProtocolOption参数，可以在这里定义

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # 构造请求参数
        params = {
            'appkey': appkey,
            'timestamp': timestamp,
            'signature': signature
        }

        # 构造请求头
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        api_endpoint = f"https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/createsession?appkey={appkey}&timestamp={timestamp}&signature={signature}"
        # 构造请求体
        payload = {
            "Header": {},
            "Payload": {
                "ReqId": req_id,
                "VirtualmanKey": virtualmankey,
                "UserId": user_id,
                "Protocol": protocol,
                "DriverType": driver_type
            }
        }

        # 如果有ProtocolOption参数，则添加到Payload中
        if protocol_option:
            payload["Payload"]["ProtocolOption"] = protocol_option

        # 发送POST请求
        # api_endpoint = "https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/createsession"
        response = requests.post(api_endpoint, headers=headers, json=payload, params=params)

        # 检查响应状态并打印结果
        if response.status_code == 200:
            print("请求成功，响应内容：")
            response_data = response.json()
            print(response_data)
            return jsonify(response_data)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    @staticmethod
    def list_session(appkey, access_token, virtualmankey):

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # 构造请求参数
        params = {
            'appkey': appkey,
            'timestamp': timestamp,
            'signature': signature
        }

        # 构造请求头
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        api_endpoint = f"https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/listsessionofvk?appkey={appkey}&timestamp={timestamp}&signature={signature}"
        # 构造请求体
        payload = {
            "Header": {},
            "Payload": {
                "ReqId": req_id,
                "VirtualmanKey": virtualmankey,
            }
        }

        # 发送POST请求
        # api_endpoint = "https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/createsession"
        response = requests.post(api_endpoint, headers=headers, json=payload, params=params)

        # 检查响应状态并打印结果
        if response.status_code == 200:
            print("请求成功，响应内容：")
            response_data = response.json()
            print(response_data)
            return jsonify(response_data)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    @staticmethod
    def detail_session(appkey, access_token, sessionid):

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # 构造请求参数
        params = {
            'appkey': appkey,
            'timestamp': timestamp,
            'signature': signature
        }

        # 构造请求头
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        api_endpoint = f"https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/statsession?appkey={appkey}&timestamp={timestamp}&signature={signature}"
        # 构造请求体
        payload = {
            "Header": {},
            "Payload": {
                "ReqId": req_id,
                "SessionId": sessionid,
            }
        }

        # 发送POST请求
        response = requests.post(api_endpoint, headers=headers, json=payload, params=params)

        # 检查响应状态并打印结果
        if response.status_code == 200:
            print("请求成功，响应内容：")
            response_data = response.json()
            print(response_data)
            return jsonify(response_data)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    @staticmethod
    def start_session(appkey, access_token, sessionid):

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # 构造请求参数
        params = {
            'appkey': appkey,
            'timestamp': timestamp,
            'signature': signature
        }

        # 构造请求头
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        api_endpoint = f"https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/startsession?appkey={appkey}&timestamp={timestamp}&signature={signature}"
        # 构造请求体
        payload = {
            "Header": {},
            "Payload": {
                "ReqId": req_id,
                "SessionId": sessionid,
            }
        }

        # 发送POST请求
        response = requests.post(api_endpoint, headers=headers, json=payload, params=params)

        # 检查响应状态并打印结果
        if response.status_code == 200:
            print("请求成功，响应内容：")
            response_data = response.json()
            print(response_data)
            return jsonify(response_data)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    @staticmethod
    def close_session(appkey, access_token, sessionid):

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # 构造请求参数
        params = {
            'appkey': appkey,
            'timestamp': timestamp,
            'signature': signature
        }

        # 构造请求头
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        api_endpoint = f"https://gw.tvs.qq.com/v2/ivh/sessionmanager/sessionmanagerservice/closesession?appkey={appkey}&timestamp={timestamp}&signature={signature}"
        # 构造请求体
        payload = {
            "Header": {},
            "Payload": {
                "ReqId": req_id,
                "SessionId": sessionid,
            }
        }

        # 发送POST请求
        response = requests.post(api_endpoint, headers=headers, json=payload, params=params)

        # 检查响应状态并打印结果
        if response.status_code == 200:
            print("请求成功，响应内容：")
            response_data = response.json()
            print(response_data)
            return jsonify(response_data)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    @staticmethod
    def create_ws(appkey, access_token, virtualmankey, sessionid):

        user_id = 'f2612aa810014e8997f95bda97917268'

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp, sessionid)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # WebSocket连接地址
        ws_url = f"wss://gw.tvs.qq.com/v2/ws/ivh/interactdriver/interactdriverservice/commandchannel?appkey={appkey}&requestid={sessionid}&timestamp={timestamp}&signature={signature}"

        # 创建WebSocket连接
        ws = websocket.WebSocket()
        try:
            # 连接到服务器
            ws.connect(ws_url)
            print("ws connected")
            return ws
        except websocket.WebSocketException as e:
            print(f"Connection failed: {e}")
        finally:
            ws.close()

    @staticmethod
    def send_text(appkey, access_token, sessionid, text):

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp, sessionid)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # WebSocket连接地址
        ws_url = f"wss://gw.tvs.qq.com/v2/ws/ivh/interactdriver/interactdriverservice/commandchannel?appkey={appkey}&requestid={sessionid}&timestamp={timestamp}&signature={signature}"

        # 创建WebSocket连接
        ws = websocket.WebSocket()
        try:
            # 连接到服务器
            ws.connect(ws_url)
            print("ws connected")
            # 构建发送文本的指令
            text_command = {
                "Header": {},
                "Payload": {
                    "ReqId": req_id,  # 生成一个唯一的ReqId
                    "SessionId": sessionid,  # 会话唯一标识
                    "Command": "SEND_TEXT",  # 指定命令类型为发送文本
                    "Data": {
                        "Text": text,
                        "ChatCommand": "NotUseChat"  # 本次驱动纯文本驱动不走对话
                    }
                }
            }

            # 发送文本驱动指令
            ws.send(json.dumps(text_command))
            print(ws.recv())
        except websocket.WebSocketException as e:
            print(f"websocket error: {e}")
        finally:
            ws.close()

    @staticmethod
    def send_audio(appkey, access_token, sessionid, text, voice, model):

        # 先调用openai 获取tts stream
        audio_stream = TTSGenerator.generate_tts_stream_16(text, voice, 'wav', model)
        print("send_audio====================")
        print(audio_stream)

        # 生成请求唯一标识 ReqId
        req_id = str(uuid.uuid4()).replace('-', '')

        # 获取当前时间戳
        timestamp = str(int(time.time()))

        # 生成签名
        signature = generate_signature(appkey, access_token, timestamp, sessionid)
        # signature = generate_signature('e38267c0e86411ebb02aed82acb0ed99', 'f68f2d10ae9e4604b76fb05cf46bccec', '1646636485')
        # BfWuaC9kmaicCggXc693uK%2BsZQ8qe88O4HVQNTdwZuo%3D
        print(signature)

        # WebSocket连接地址
        ws_url = f"wss://gw.tvs.qq.com/v2/ws/ivh/interactdriver/interactdriverservice/commandchannel?appkey={appkey}&requestid={sessionid}&timestamp={timestamp}&signature={signature}"

        # 创建WebSocket连接
        ws = websocket.WebSocket()
        try:
            # 连接到服务器
            ws.connect(ws_url)
            print("ws connected")

            # Read the audio data from the byte stream
            # audio_data = audio_stream.read()


            # chunk_size = 5120

            # # Step 1: Split the raw audio bytes into chunks of specified size
            # raw_chunks = [audio_data[i:i + chunk_size] for i in range(0, len(audio_data), chunk_size)]

            # # Step 2: Encode each chunk to Base64 and send
            # for i, raw_chunk in enumerate(raw_chunks):
            #     base64_encoded_chunk = base64.b64encode(raw_chunk).decode('utf-8')
            #     # print(f"Chunk {i + 1}: {base64_encoded_chunk}")
            #     print(f"Chunk {i + 1}")

            #     isFinal = (i == len(raw_chunks) - 1)
            #     # 构建发送音频的指令
            #     audio_command = {
            #         "Header": {},
            #         "Payload": {
            #             "ReqId": req_id,  # 生成一个唯一的ReqId
            #             "SessionId": sessionid,  # 会话唯一标识
            #             "Command": "SEND_AUDIO",  # 指定命令类型为发送文本
            #             "Data": {
            #                 "Audio": base64_encoded_chunk,
            #                 "Seq": i + 1,
            #                 "IsFinal": isFinal
            #             }
            #         }
            #     }
            #     # 发送音频驱动指令
            #     ws.send(json.dumps(audio_command))
            #     print(ws.recv())
                #time.sleep(0.12)

            chunk_size = 5120  # 每次读取512字节
            seq = 1  # 初始化序列号

            while True:
                audio_chunk = audio_stream.read(chunk_size)
                if not audio_chunk:
                    break  # 如果没有更多数据，则退出循环

                base64_encoded_chunk = base64.b64encode(audio_chunk).decode('utf-8')
                print(f"Chunk {seq}")

                # 构建发送音频的指令
                audio_command = {
                    "Header": {},
                    "Payload": {
                        "ReqId": req_id,  # 生成一个唯一的ReqId
                        "SessionId": sessionid,  # 会话唯一标识
                        "Command": "SEND_AUDIO",  # 指定命令类型为发送文本
                        "Data": {
                            "Audio": base64_encoded_chunk,
                            "Seq": seq,
                            "IsFinal": False  # 默认不是最后一块
                        }
                    }
                }

                # 如果是最后一块数据，设置IsFinal为True
                if len(audio_chunk) < chunk_size:
                    audio_command["Payload"]["Data"]["IsFinal"] = True

                # 发送音频驱动指令
                ws.send(json.dumps(audio_command))
                print(ws.recv())

                seq += 1  # 增加序列号

        except websocket.WebSocketException as e:
            print(f"websocket error: {e}")
        finally:
            ws.close()
