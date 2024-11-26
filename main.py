import os
import uuid
import json
import aiohttp
import argparse
from datetime import datetime, timezone
from fake_useragent import UserAgent
from colorama import *
import random  # Menambahkan bagian import di awal file
import logging
import asyncio  # Make sure asyncio is imported
from colorama import init, Fore, Style

# Initialize colorama for proper coloring on different platforms (especially Termux)
init(autoreset=True)

# Define color variables
green = Fore.LIGHTGREEN_EX
red = Fore.LIGHTRED_EX
magenta = Fore.LIGHTMAGENTA_EX
white = Fore.LIGHTWHITE_EX
black = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
yellow = Fore.LIGHTYELLOW_EX

# The rest of your code goes here

# Set up logging to file
logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

class Grass:
    def __init__(self, userid, proxy):
        self.userid = userid
        self.proxy = proxy
        self.ses = aiohttp.ClientSession()
        self.connection_duration = (60 * 60 * 3) + 20  # Set connection duration for 3 hours

    def log(self, msg):
        now = datetime.now(tz=timezone.utc).isoformat(" ").split(".")[0]
        print(f"{black}[{now}] {reset}{msg}{reset}")

    @staticmethod
    async def ipinfo(proxy=None):
        try:
            async with aiohttp.ClientSession() as client:
                result = await client.get("https://api.ipify.org/", proxy=proxy)
                result.raise_for_status()  # Raises exception for 4xx/5xx status codes
                return await result.text()
        except Exception as e:
            logging.error(f"Error in ipinfo: {str(e)}")
            return None

    def log_error(self, error_msg):
        try:
            logging.error(f"{datetime.now(tz=timezone.utc).isoformat()} - {error_msg}")
        except Exception as e:
            print(f"Logging error: {str(e)}")

    async def start(self):
        max_retry = 10
        retry = 1
        proxy = self.proxy
        if proxy is None:
            proxy = await Grass.ipinfo()
            if not proxy:
                self.log_error("Failed to retrieve proxy IP, aborting connection.")
                return

        browser_id = uuid.uuid5(uuid.NAMESPACE_URL, proxy)
        useragent = UserAgent().random
        headers = {
            "Host": "proxy2.wynd.network:4650",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": useragent,
            "Upgrade": "websocket",
            "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi",
            "Sec-WebSocket-Version": "13",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        }
        while True:
            try:
                if retry >= max_retry:
                    self.log(f"{yellow}Maximum retries reached, skipping proxy...")
                    await self.ses.close()
                    return

                self.log(f"{self.userid} is attempting to connect to the server...")
                async with self.ses.ws_connect(
                    "wss://proxy2.wynd.network:4650/",
                    headers=headers,
                    proxy=self.proxy,
                    timeout=1000,
                    autoclose=False,
                ) as wss:
                    res = await wss.receive_json()
                    auth_id = res.get("id")
                    if auth_id is None:
                        self.log(f"{red}auth id is None")
                        return None

                    auth_data = {
                        "id": auth_id,
                        "origin_action": "AUTH",
                        "result": {
                            "browser_id": str(browser_id),
                            "user_id": self.userid,
                            "user_agent": useragent,
                            "timestamp": int(datetime.now().timestamp()),
                            "device_type": "extension",
                            "version": "4.26.2",
                            "extension_id": "lkbnfiajjmbhnfledhphioinpickokdi",
                        },
                    }
                    await wss.send_json(auth_data)
                    self.log(f"{green}Successfully connected {white}to the server!")
                    retry = 1
                    connection_start_time = datetime.now()
                    while True:
                        if (datetime.now() - connection_start_time).total_seconds() >= self.connection_duration:
                            self.log(f"{yellow}Connection has lasted for {self.connection_duration/3600} hours, preparing to reconnect...")
                            break

                        ping_data = {
                            "id": str(uuid.uuid4()),
                            "version": "1.0.0",
                            "action": "PING",
                            "data": {},
                        }
                        await wss.send_json(ping_data)
                        self.log(f"{white}Sending {green}ping {white}to server!")
                        pong_data = {"id": "F3X", "origin_action": "PONG"}
                        await wss.send_json(pong_data)
                        self.log(f"{white}Sending {magenta}pong {white}to server!")
                        await countdown(120)
            except KeyboardInterrupt:
                await self.ses.close()
                exit()
            except Exception as e:
                self.log_error(f"Error occurred: {str(e)}")
                retry += 1
                if retry >= max_retry:
                    self.log(f"{yellow}Maximum retries reached, skipping proxy...")
                    await self.ses.close()
                    return
                continue

async def countdown(t):
    for i in range(t, 0, -1):
        minute, seconds = divmod(i, 60)
        hour, minute = divmod(minute, 60)
        seconds = str(seconds).zfill(2)
        minute = str(minute).zfill(2)
        hour = str(hour).zfill(2)
        print(f"Waiting for {hour}:{minute}:{seconds} ", flush=True, end="\r")
        await asyncio.sleep(1)

async def main():
    arg = argparse.ArgumentParser()
    arg.add_argument(
        "--proxy", "-P", default="proxies.txt", help="Custom proxy input file"
    )
    args = arg.parse_args()
    os.system("cls" if os.name == "nt" else "clear")

    token = open("token.txt", "r").read()
    userid = open("userid.txt", "r").read()
    if len(userid) <= 0:
        print(f"{red}Error: {white}Please enter your user ID first!")
        exit()
    if not os.path.exists(args.proxy):
        print(f"{red}{args.proxy} not found, please ensure {args.proxy} is available!")
        exit()
    proxies = open(args.proxy, "r").read().splitlines()
    if len(proxies) <= 0:
        proxies = [None]
    
    # Adding delay and log for task creation
    tasks = []
    total_proxies = len(proxies)
    
    for index, proxy in enumerate(proxies, 1):
        # Adding random delay between 2-10 seconds for each proxy
        delay = random.uniform(2, 10)
        tasks.append(asyncio.create_task(Grass(userid, proxy).start()))
        print(f"{green}Proxy task {index}/{total_proxies} created{reset}")

        if index != total_proxies:
            print(f"{white}Waiting {green}{delay:.2f} seconds{white} before creating task for proxy {index+1}")
            await asyncio.sleep(delay)
        
    print(f"{magenta}All proxy tasks created, starting execution...{reset}")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
