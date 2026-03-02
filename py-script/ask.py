# -*- coding=utf-8 -*-
"""
访问 TapDB「AI洞察」服务的 websocket 客户端。
"""
import re
import subprocess
import sys
import threading
import time
import uuid
import json
import traceback
from urllib.parse import urlparse, urlunparse

from common_arg import CommonArgumentParser

# 定义需要的包
required_packages = {
    "websocket": "websocket-client",
}
for modelname, pkg in required_packages.items():
    try:
        __import__(modelname)
    except ImportError:
        print(f"检测到缺少包 {pkg}，正在自动安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import websocket  # noqa: E402


class AIInsightWSApp(websocket.WebSocketApp):
    __slots__ = ['conversation_id',
                 'message_id',
                 'request_id',
                 'parent_message_id',
                 'question',
                 'answer_parts',
                 'answer_images',
                 'answer_footnotes']

    def __init__(self,*args,**kwargs):
        super(AIInsightWSApp,self).__init__(*args,**kwargs)
        self.request_id = None
        self.conversation_id = None
        self.message_id = None
        self.parent_message_id = None
        self.question = None
        self.answer_parts = []
        self.answer_images = []
        self.answer_footnotes = []



def parse_args(argv=None):
    parser = CommonArgumentParser(prog="ask")
    parser.add_argument(
        "-c",
        "-conversation_id",
        "--conversation_id",
        dest="conversation_id",
        type=str,
        default=None,
        help="可选：会话ID",
    )
    parser.add_argument(
        "-q",
        "-question",
        "--question",
        dest="content",
        type=str,
        required=True,
        help="必填：提问内容",
    )

    parser.add_argument(
        "-p",
        "-parent_message_id",
        "--parent_message_id",
        dest="parent_message_id",
        type=str,
        default=None,
        help="可选：父消息ID",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    _args = parse_args(argv)

    def on_message(ws, message):
        ws : AIInsightWSApp
        try:
            arr = json.loads(message)
            code = arr[0]
            if code == 'heartbeat':
                return
            print(f"## WS 收到消息 : {message}")
            if code != 'data':
                print(f"无法识别的code : {code}")
                return

            data_body = arr[1]
            requestId = data_body['requestId']
            if requestId != ws.request_id:
                print(f"服务端返回的request id ({requestId}) 不等于本地值({ws.request_id})")
                return

            status = data_body['status']
            if status != 'success':
                print(f"服务端返回的status不是success : {status}")
                return
            in_data = data_body['data']


            event_type = in_data.get('event_type','NA')
            if event_type not in ["progress"]:

                if event_type == "done":
                    finish_reason = in_data.get('finish_reason', "Unknown")
                    if finish_reason != 'complete':
                        print(f"服务端返回的finish_reason不是complete : {finish_reason}")
                    ws.close()
                    return

            if 'fragment' not in in_data:
                return
            fragment = in_data['fragment']
            if 'append_answer' not in fragment:
                return
            append_answer : dict = fragment['append_answer']
            text = append_answer['text']
            images = append_answer['images']
            references = append_answer['references']
            codeblocks = append_answer['codeblocks']


            if text:
                ws.answer_parts.append(text)
            if references:
                for reference in references:
                    title = reference['link']['title']
                    url = reference['link']['uri']
                    ws.answer_parts.append(f"\n[{title}]({url})\n")


        except:
            traceback.print_exc()
            print(f"<ERROR>\n")
            print(f"消息解析错误 : {message}")
            print(f"\n</ERROR>")
            ws.close()
        # ws.close()

    def on_error(ws, error):
        err_str = f"{error}".strip()
        if not err_str:
            return
        print(f"<ERROR>\n")
        print(error)
        print(f"\n</ERROR>")
        try:
            ws.close()
        except:
            pass

    def on_close(_ws, close_status_code, close_msg):
        print("### 连接已关闭 ###")
        if close_status_code:
            print(f"关闭状态码: {close_status_code}")
        if close_msg:
            print(f"关闭原因: {close_msg}")

    def heartbeat_sender(ws):
        while ws.keep_running:
            try:
                time.sleep(10)  # 心跳间隔
                ws.send('["heartbeat",""]')
            except Exception as e:
                print(f"心跳发送失败: {e}")
                break

    def on_open(ws):
        print(f"## WS 连接已经建立")
        thread = threading.Thread(target=heartbeat_sender, args=(ws,))
        thread.daemon = True  # 确保主程序退出时线程也退出
        thread.start()

        ws : AIInsightWSApp
        d = {
            "requestId": ws.request_id,
            "params": {
                "action": "ask",
                "question": ws.question,
                "add_insight": False,
                "thinking_mode": "normal",
                "is_core_user": False,
                "projectIds": [],
                "model": "claude",
                "conversation_id": ws.conversation_id,
                "message_id": ws.message_id
            }
        }

        if ws.parent_message_id:
            d["params"]["parent_message_id"] = ws.parent_message_id


        json_str = json.dumps(["data",d], indent=4, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

        ws.send(json_str)



    print(f"args : {_args}")
    ws_url = f"wss://{_args.endpoint}/ad-plus/api/ws/conversation"
    print(f"连接ws : {ws_url}")
    ws = AIInsightWSApp(
        ws_url,
        header={
            "MCP-KEY" : _args.mcp_key,
        },
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.parent_message_id = _args.parent_message_id
    ws.request_id = str(uuid.uuid4())
    ws.message_id = str(uuid.uuid4())
    ws.conversation_id = _args.conversation_id or str(uuid.uuid4())
    ws.question = _args.content

    ws.run_forever()

    output_text = "".join(ws.answer_parts)
    output_text = re.sub(r'\n+', '\n', output_text)
    print(f"<CONVERSATION_ID>{ws.conversation_id}</CONVERSATION_ID>")
    print(f"<MESSAGE_ID>{ws.message_id}</MESSAGE_ID>")
    print("<ANSWER>")
    print(output_text)
    print("</ANSWER>")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

