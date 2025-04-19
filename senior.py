from calendar import c
from unicodedata import category
from openai import OpenAI
import requests
import time
import qrcode
from PIL import Image
import hashlib
import random
import string

tiku_mode = False # 刷题库模式，调试使用
modify_ck = "" # 覆盖CK，调试使用
user_tiku_report = False

def get_whksoft_token():
    salt = 'zFSiZqkU1Oxfs3oh0UtlBGLsqKQIEdU6'
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    ts = int(time.time() * 1000)
    hash = hashlib.md5(f"&s={salt}&t={ts}&n={nonce}".encode()).hexdigest()
    return f"{ts},{nonce},{hash}"

def report_tiku(qid, category,question,ans_1,ans_2,ans_3,ans_4,source,correct_answer):
    print("正在提交题目...")
    data = {
        "qid": qid,
        "question": question,
        "title": question,# compatible with whksoft
        "ans_1": ans_1,
        "ans_2": ans_2,
        "ans_3": ans_3,
        "ans_4": ans_4,
        "answer": correct_answer,
        "type": 0, # compatible with whksoft
        "optionA": ans_1,# compatible with whksoft
        "optionB": ans_2,# compatible with whksoft
        "optionC": ans_3,# compatible with whksoft
        "optionD": ans_4,# compatible with whksoft
        "source": source,
        "time": int(time.time() * 1000),# compatible with whksoft
        "category": category,
        "tag": category,# compatible with whksoft
    }
    # req = session.post(
    #    "https://api-q.whksoft.cn/question/add?token="+get_whksoft_token(), json=data,headers={
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    #         "Content-Type": "application/json",
    #         "Authorization": "Basic d2hrc29mdDp3aGsxMjM0NQ==",
    #     },
    #     verify=False
    # )
    # if req.status_code == 200:
    #     print("提交成功")
    #     print(req.text)
    # else:
    #     print("提交失败")
    #     print(req.text)
    try:
        req = session.post(
        "https://senior.ziantt.top/submit", json=data,
        headers={
                "User-Agent": "Bilibili Senior Script Report/1.0", 
        }
        ).json()
        if req["status"] == "success":
            print("题库服务器提交成功")
        elif req["status"] == "exist":
            print("题目已存在")
        else:
            print("题库服务器提交失败")
            print(req)
    except Exception as e:
        print("题库服务器提交失败")
        print(e)

def qr_login():
    print("由BHYG提供登录支持")
    generate = session.get(
        "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    )
    generate = generate.json()
    if generate["code"] == 0:
        url = generate["data"]["url"]
    else:
        print(generate)
        return
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.print_ascii(invert=True)
    img = qr.make_image()
    img.show()
    print("请使用手机扫描二维码")
    while True:
        time.sleep(1)
        url = (
            "https://passport.bilibili.com/x/passport-login/web/qrcode/poll?source=main-fe-header&qrcode_key="
            + generate["data"]["qrcode_key"]
        )
        req = session.get(url, headers=headers)
        # read as utf-8
        check = req.json()["data"]
        if check["code"] == 0:
            print("登录成功")
            break
        elif check["code"] == 86101:
            pass
        elif check["code"] == 86090:
            print(check["message"])
        elif check["code"] == 86083:
            print(check["message"])
            return qr_login(session, headers)
        elif check["code"] == 86038:
            print(check["message"])
            return qr_login(session, headers)
        else:
            print(check)
            return qr_login(session, headers)
    return

session = requests.Session()
headers = {
    "Cookie": modify_ck,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}
session.headers.update(headers)

if modify_ck == "":
    qr_login()
    cookie = session.cookies.get_dict()
    headers["Cookie"] = "; ".join([f"{k}={v}" for k, v in cookie.items()])

print("请输入LLM端点，留空则使用DeepSeek")
llm_endpoint = input()
if llm_endpoint == "":
    llm_endpoint = "https://api.deepseek.com"
print("请输入LLM密钥(通常为sk-xxxx)")
llm_key = input()
if llm_key == "":
    print("请添加LLM密钥")
    exit(0)
print("请输入模型名称，留空则采用DeepSeekV3")
model_name = input()
if model_name == "":
    model_name = "deepseek-chat"

try:
    client = OpenAI(api_key=llm_key, base_url=llm_endpoint)
    client.models.retrieve(model_name)
except Exception as e:
    print("LLM连接失败，请检查LLM密钥和端点是否正确")
    print(e)
    exit(0)

while True:
    user_tiku_report_prompt = input("本项目已参与题目补全计划，请确认是否愿意参与计划（完全匿名，不用担心隐私泄露）请输入（y/n）")
    user_tiku_report_prompt = user_tiku_report_prompt.lower()
    if user_tiku_report_prompt == "y":
        user_tiku_report = True
        break
    elif user_tiku_report_prompt == "n":
        user_tiku_report = False
        break
    else:
        print("输入错误，请重新输入")

if "bili_jct" in headers["Cookie"]:
        csrf = headers["Cookie"].split("bili_jct=")[1].split(";")[0]
else:
    print("请在headers中添加bili_jct(csrf)")
    exit(0)

# {'code': 0, 'message': '0', 'ttl': 1, 'data': {'categories': [{'id': 1, 'name': '动画/漫画'}, {'id': 2, 'name': '知识'}, {'id': 3, 'name': '影视'}, {'id': 4, 'name': '音乐'}, {'id': 5, 'name': '鬼畜'}, {'id': 6, 'name': '文史'}, {'id': 7, 'name': '游戏'}, {'id': 8, 'name': '体育'}]}}
# check eligibility
resp = session.get("https://api.bilibili.com/x/senior/v1/entry", headers=headers).json()
if resp["data"]["eligible"] == False:
    print("您不是Lv6用户，无法使用此脚本")
    # resp = session.get("https://api.bilibili.com/x/senior/v1/answer/rule", headers=headers).json()
    # print(resp)
    # # {'code': 0, 'message': '0', 'ttl': 1, 'data': {'rules': [{'heading': '什么是硬核会员试炼？', 'paragraph': [{'text': '硬核会员试炼，是我们为LV6用户设计的专属挑 战。挑战通过后，能解锁特殊的LV6标识、“硬核会员”称号和权益。'}, {'text': '硬核会员有效期为365天，若365天期满，需重新参与。'}]}, {'heading': '硬核会员有什么权益 ？', 'paragraph': [{'text': '硬核专属举报功能', 'is_new': True}, {'text': '专属三连推荐', 'is_new': True}, {'text': '生日定制彩蛋', 'is_new': True}, {'text': '社区实验室 —— 硬核会员弹幕模式'}, {'text': '特别关注、黑名单上限翻倍'}, {'text': 'LV6试炼出题权'}]}, {'heading': '我怎么才能通过这个测试？', 'paragraph': [{'text': '120min内，答对60道及以上的题目（最多可答100道题），即可通过。\n注意：每24h，最多有3次挑战的机会。'}]}, {'heading': '更多说明', 'paragraph': [{'text': '“ 硬核会员”与“大会员”无关，目前仅通过试炼才能获得该称号。'}, {'text': '若发现您在测试过程中使用非正常技术手段，您可能会被永久禁止参与挑战。'}, {'text': '若您出现了违反社区规范的行为，您的“硬核会员”资格可能会被人工核实后取消。'}]}]}}
    # resp = session.get("https://api.bilibili.com/x/senior/v1/entry", headers=headers).json()
if "stage" not in resp["data"] or resp["data"]["stage"] == 0 or resp["data"]["stage"] == 1:
    print("默认选择：知识区")
    ids = "2"
    while True:
        resp = session.get("https://api.bilibili.com/x/senior/v1/captcha", headers=headers).json()
        if resp["data"]["type"] != "bilibili":
            print("请在手机上完成极验验证")
            exit(0)
        token = resp["data"]["token"]
        url = resp["data"]["url"]
        print("请完成图片验证码："+url)
        img = session.get(url)
        with open("captcha.jpg", "wb") as f:
            f.write(img.content)
        img = Image.open("captcha.jpg")
        img.show()
        captcha = input("请输入验证码(留空刷新):")
        if captcha == "":
            continue
        else:
            break
    data = {
        "ids": ids,
        "type": "bilibili",
        "bili_token": token,
        "bili_code": captcha,
        "gt_challenge": "",
        "gt_validate": "",
        "gt_seccode": "",
        "csrf": csrf
    }
    capt_resp = session.post("https://api.bilibili.com/x/senior/v1/captcha/submit", headers=headers, data=data).json()
elif resp["data"]["stage"] == 3:
    print("您已经答题完成")
    exit()

qid_o = 0
try:
    url = "https://api.bilibili.com/x/senior/v1/answer/result"
    resp = session.get(url, headers=headers).json()
    current_score = resp["data"]["score"]
except Exception as e:
    print("获取用户信息失败")
    print(e)
    exit(0)
try:
    while True:
        print()
        try:
            url = "https://api.bilibili.com/x/senior/v1/question"
            data = session.get(url, headers=headers).json()
            q_data = data
        except Exception as e:
            print("获取题目失败")
            print(e)
            time.sleep(1)
            continue
        qid = data["data"]["id"]
        q_s_time = time.time()
        if qid == qid_o:
            continue
        qid_o = qid
        q_order = data["data"]["question_num"]
        print("题号："+str(q_order))
        print("当前题目id："+str(qid))
        print("当前题目："+data["data"]["question"])
        for i in data["data"]["answers"]:
            print(i["ans_text"])
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "接下来你将作为答题机器人，根据我给定的json，回答最正确的答案，你只需要给出你认为的ans_text即可（而非ans_hash），不要回复任何其他内容"},
                    {"role": "user", "content": str(data["data"])},
                ],
                stream=False
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print("LLM连接失败，请检查LLM密钥和端点是否正确")
            print(e)
            exit(0)
        for i in data["data"]["answers"]:
            if i["ans_text"] == answer:
                ans_hash = i["ans_hash"]
                break
        if ans_hash == None:
            print("无法找到答案，大模型重试中。。。")
            continue
        try:
            url = "https://api.bilibili.com/x/senior/v1/answer/submit"
            data = {
                "ans_hash": ans_hash,
                "id": qid,
                "ans_text": answer,
                "csrf": csrf
            }
            resp = session.post(url, headers=headers, data=data).json()
            if q_order >= 40 and tiku_mode:
                print("题库模式防通过")
                exit()
            if q_order >= 100:
                print("答题完成")
            if resp["code"] == 0:
                print("答题成功")
                print("耗时："+str(time.time()-q_s_time))
                correct_flag = False
                while True:
                    try:
                        url = "https://api.bilibili.com/x/senior/v1/answer/result"
                        resp = session.get(url, headers=headers).json()
                        if resp["data"]["score"] > current_score:
                            correct_flag = True
                            print("回答正确")
                            current_score = resp["data"]["score"]
                        else:
                            print("回答错误")
                        break
                    except Exception as e:
                        print("获取用户信息失败")
                        print(e)
                if tiku_mode or user_tiku_report:
                    correct_answer = answer if correct_flag else None
                    print(q_data)
                    report_tiku(qid, "2", q_data["data"]["question"],
                        q_data["data"]["answers"][0]["ans_text"], q_data["data"]["answers"][1]["ans_text"], q_data["data"]["answers"][2]["ans_text"], q_data["data"]["answers"][3]["ans_text"],
                        q_data["data"]["source"], correct_answer
                    )
            elif resp["code"] == 41105:
                print("答题完成")
                break
            elif resp["code"] == 41104:
                print("答题过快")
            elif resp["code"] == 41103:
                print("已回答过")
        except Exception as e:
            print("答题失败")
            print(e)
except KeyboardInterrupt:
    print("检测到取消指令脚本已停止")

url = "https://api.bilibili.com/x/senior/v1/answer/result"
resp = session.get(url, headers=headers).json()
score = resp["data"]["score"]
chance = resp["data"]["chance"]
url = "https://api.bilibili.com/x/senior/v1/member/info"
resp = session.get(url, headers=headers).json()
senior_member = resp["data"]["senior_member"]
print("\n-------------")
print("当前分数："+str(score))
print("当前剩余挑战次数："+str(chance))
print("是否为硬核会员："+str(senior_member))
