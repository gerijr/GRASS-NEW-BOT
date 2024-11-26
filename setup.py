import json
import httpx


async def main():
    ses = httpx.AsyncClient()
    email = input("[?] 请输入你的邮箱 : ")
    password = input("[?] 请输入你的密码 : ")
    login_url = "https://api.getgrass.io/login"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99", "Microsoft Edge WebView2";v="130"',
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "origin": "http://tauri.localhost",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "http://tauri.localhost/",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
    }
    res = await ses.post(
        login_url, headers=headers, json={"username": email, "password": password}
    )
    if res.status_code != 200:
        print("[x] faile to login,try again later !")
        return
    token = res.json().get("result", {}).get("data", {}).get("accessToken")
    userid = res.json().get("result", {}).get("data", {}).get("userId")

    if token is None:
        print("[x] failed get access token,try again later !")
        return
    open("userid.txt", "w").write(userid)
    open("token.txt", "w").write(token)
    print(f"[+] sucess login, now run main.py !")


if __name__ == "__main__":
    try:
        import asyncio

        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
