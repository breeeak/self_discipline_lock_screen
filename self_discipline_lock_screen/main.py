# -*- coding: utf-8 -*-
# @Time    : 2022/1/5 17:42
# @Author  : Marshall
# @FileName: main.py
import PySimpleGUI as sg
import base64
import ctypes
import time
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
import random
import gc
import psutil
import pyautogui as pag
import threading

from utils import *


def deal_time(config):
    time_tag = time.strftime("%Y-%m-%d", time.localtime())
    time_intervals = config["time_intervals"]
    begin_time_stamps = []
    end_time_stamps = []
    if len(time_intervals) > 0:
        for i in range(len(time_intervals)):
            try:
                begin_time_str = time_tag + " " + time_intervals[i][0]
                end_time_str = time_tag + " " + time_intervals[i][1]
                begin_time_stamp = int(time.mktime(time.strptime(begin_time_str, "%Y-%m-%d %H:%M:%S")))
                end_time_stamp = int(time.mktime(time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")))
                if end_time_stamp > begin_time_stamp:
                    begin_time_stamps.append(begin_time_stamp)
                    end_time_stamps.append(end_time_stamp)
                else:
                    print("请检查时间设置,结束时间应该大于开始时间")
            except Exception:
                print("请检查时间设置")
    if all(x <= y for x, y in zip(begin_time_stamps, begin_time_stamps[1:])) and all(
            x <= y for x, y in zip(end_time_stamps, end_time_stamps[1:])):
        return begin_time_stamps, end_time_stamps
    else:
        print("请检查时间设置,时间段设置应从早到晚")
    # return begin_time_stamps, end_time_stamps # 不返回值 强制报错


def interval_recording(config):
    video_img, have_face = face_detect()
    screen_img = screen_capture()

    cur = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))[11:]
    video_img_name = os.path.join(config["out_dir"], "video_capture_" + cur + ".png")
    screen_img_name = os.path.join(config["out_dir"], "screen_capture_" + cur + ".png")
    cv2.imwrite(video_img_name, video_img)
    cv2.imwrite(screen_img_name, screen_img)
    content = "\n![截图](video_capture_" + cur + ".png)\n![截图](screen_capture_" + cur + ".png)"
    if have_face:
        content = content + "\n#### 有在学习"
    else:
        content = content + "\n#### 好像没有学习哦"
        if config["is_reminder"] == "1":
            speech(config["reminder"])
    with open(config["md_path"], "a+", encoding="utf-8") as f:
        f.write(content)
    print("执行定时任务，截图，截取屏幕摄像头等", cur)


def do_schedule(config):
    print("设定定时任务")
    interval = int(config["interval"]) * 60
    sched = BackgroundScheduler(timezone='GMT')
    sched.add_job(interval_recording, 'interval', args=[config], seconds=interval, id="interval_recording")
    sched.start()
    return sched, True


def pause_schedule(sched):
    print("中止定时任务")
    sched.pause_job("interval_recording")


def resume_schedule(sched):
    print("继续定时任务")
    sched.resume_job("interval_recording")




def config_parser(config_path="./config/config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        load_dict = json.load(f)
    pass
    return load_dict


def rest_gui():
    layout = [
        [sg.Text("离开座位，休息一会儿吧", size=(30, 1), justification='center', text_color="#000", font=("Helvetica", 60))],
    ]
    top_window = sg.Window('Rest GUI', layout, finalize=True, keep_on_top=True, grab_anywhere=False,
                           transparent_color=sg.theme_background_color(), no_titlebar=True, element_justification='c')
    return top_window


def start_gui(config, end=False):
    title = config["start_title"]
    tips = config["start_tips"]
    if end:
        title = config["end_title"]
        tips = config["end_tips"]
    layout = [
        [sg.Text(title, size=(30, 1), justification='center', text_color="#000", font=("Helvetica", 60))],
        [sg.Text(tips, font=("宋体", 40), text_color="#000")],
        [sg.Multiline(size=(50, 5), key='plan')],
        [sg.Button('确定', size=(10, 1), key='set_plan')],
    ]
    top_window = sg.Window('Everything bagel', layout, finalize=True, keep_on_top=True, grab_anywhere=False,
                           transparent_color=sg.theme_background_color(), no_titlebar=True, element_justification='c')
    return top_window


def background_gui(config):
    """
    每次生成一个随机背景的全屏窗口
    """
    x = random.randint(0, len(os.listdir(config["background_pth"]))-1)
    img_name = os.listdir(config["background_pth"])[x]
    img_path = os.path.join(config["background_pth"], img_name)
    if img_name.endswith(".jpg") or img_name.endswith(".jpeg"):
        img = cv2.imread(img_path)
        img_path = img_path.split(".")[0] + ".png"
        cv2.imwrite(img_path, img)
    with open(img_path, "rb") as f:
        # b64encode是编码，b64decode是解码
        background_image = base64.b64encode(f.read())

    background_layout = [[sg.Image(data=background_image, size=config["screensize"])]]
    window_background = sg.Window('Background', background_layout, no_titlebar=True, finalize=True, margins=(0, 0),
                                  element_padding=(0, 0), size=config["screensize"], alpha_channel=.6)
    return window_background


def rest(config, time_span):
    # 初始化界面
    background_window = background_gui(config)
    rest_window = rest_gui()
    _, have_face = face_detect()
    if have_face:
        speech(config["reminder_rest"])
    while True:
        window, event, values = sg.read_all_windows(timeout=200)
        print(event, values)
        if event is None or event == 'Cancel' or event == 'Exit':
            print(f'closing window = {window.Title}')
            break
        current_timestamp = int(time.time())
        _, have_face = face_detect()
        if have_face:
            speech(config["reminder_rest"])
        else:
            config["unlearning_num"] = config["unlearning_num"] + 1
        if current_timestamp > time_span[-1]:
            break

    rest_window.close()
    background_window.close()


def start_up(config, end=False):
    # 初始化界面
    background_window = background_gui(config)
    lockscreen_window = start_gui(config, end=end)
    while True:
        window, event, values = sg.read_all_windows()
        print(event, values)
        if event is None or event == 'Cancel' or event == 'Exit':
            print(f'closing window = {window.Title}')
            break
        if event is "set_plan":
            # 写入计划到md中,就关闭这个启动界面
            if len(values["plan"]) > 0:
                if os.path.exists(config["md_path"]):
                    content = "\n\n" + config["md_title"] + "### 今日计划,重启\n\n" + values["plan"] + "\n\n"
                    if end:
                        content = "\n" + config["md_title"] + "### 今日总结\n\n" + str(config["unlearning_num"]) + "次，未在学习 \n\n" + values["plan"] + "\n"
                    with open(config["md_path"], "a+", encoding="utf-8") as f:
                        f.write(content)
                else:
                    content = config["md_title"] + "### 今日计划\n\n" + values["plan"] + "\n\n"
                    with open(config["md_path"], "w", encoding="utf-8") as f:
                        f.write(content)
                break
            else:
                # 没有输入提示
                sg.popup_ok("请输入计划！", keep_on_top=True)
    lockscreen_window.close()
    background_window.close()


def do_detect_games(config):
    flag = True
    times = 1
    while flag:
        print("正在检测是否在玩游戏")
        time.sleep(2)
        pl = psutil.pids()
        for pid in pl:
            if psutil.Process(pid).name() in config["game_names"]:
                times = times + 1
                print("正在游戏！")
                # 如果大于60分钟就结束该进程
                if times > config["game_time"]:
                    sg.popup_error("游戏时间已结束！", keep_on_top=True)
                    os.popen('taskkill.exe /pid:' + str(pid))


def do_job(path = "2022-01-26-16-16-53"):
    """
    打开QQ连续发送消息，模拟震动，没有时间做个智能手环了
    """
    key_event = []
    global FLAG
    for file in os.listdir(path):
        if file.endswith("txt"):
            with open(os.path.join(path, file), 'r') as f:
                for content in f.readlines():
                    content = content.strip()
                    if content != "":
                        key_steps = content.split(":")
                        key_event.append(key_steps)
    # ['11', 'Button.left', '1643,20', '1643181849', '2022-01-26-15-23-55\\STEP_11.png']
    for i, step in enumerate(key_event):
        if step[1] == "Button.left" or step[1] == "Button.right":
            location = pag.locateOnScreen(step[-1])     # TODO 许多有hover，颜色会变无法实现，先默认点击上一次的绝对位置
            location = step[2].split(",")
            x = int(location[0])
            y = int(location[1])
            if step[1] == "Button.left":
                pag.click(x, y)
            else:
                pag.click(x, y, button="right")
            # if location:
            #     x, y = pag.center(location)
            #     time.sleep(0.1)
            #     if step[1] == "Button.left":
            #         pag.click(x, y)
            #     else:
            #         pag.click(x, y, button="right")
        elif step[1] == "key" and step[2] != "Key.ctrl_l":   # 键盘事件
            if step[2].startswith("Key."):
                pag.press(step[2].replace("Key.", ""))
            else:
                content = step[2].replace("'", "")
                if content == "1":
                    num = 0
                    while FLAG:
                        num = num + 1
                        time.sleep(3)
                        pag.typewrite(str(num))
                        pag.hotkey("ctrl", "enter")
                    return
        if i == 0:
            time.sleep(15)
        else:
            time.sleep(2)
    print(key_event)

def push_getup():
    # TODO 连接智能手表，震动起床叫醒
    k_thread = threading.Thread(target=do_job)
    k_thread.start()
    print("已启动服务")
    pass


def push_getup_end():
    # TODO 连接智能手表，停止震动
    print("push_getup_end")
    global FLAG
    FLAG = False
    pass


def do_alarm(config):
    global FLAG
    flag = True
    push_success = False
    while flag:
        time.sleep(5)
        _, have_face = face_detect()
        if have_face:
            flag = False
            FLAG = False
            push_getup_end()
        else:
            if not push_success:
                push_getup()
                push_success = True
            config["unlearning_num"] = config["unlearning_num"] + 1
        pass


def main():
    config = config_parser()
    # 为config 添加一些公用信息
    # 定义log的信息
    config["time_tag"] = time.strftime("%Y-%m-%d", time.localtime())
    config["out_dir"] = os.path.join('log', config["time_tag"])
    if not os.path.exists(config["out_dir"]):
        os.mkdir(config["out_dir"])
    config["md_path"] = os.path.join(config["out_dir"], "log.md")
    config["md_title"] = "## " + config["time_tag"] + "\n\n"
    # 定义窗口的大小
    user32 = ctypes.windll.user32
    config["screensize"] = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    # 定义背景样式
    config["background_pth"] = "img"
    # 未在学习的次数，记录到md中
    config["unlearning_num"] = 0
    # 起床叫醒
    do_alarm(config)

    # 启动窗口，输入今日计划
    start_up(config)

    # 获取记录的时间，并改为时间戳格式
    begin_time_stamps, end_time_stamps = deal_time(config)
    # 无论如何都先创建一个定时任务，这个定时任务不会立即执行，而是在经过时间间隔后才执行
    scheduler, can_pause = do_schedule(config)  # can pause 是为了任务只停止一次
    # 一直激活程序，当时间到了就暂停任务
    while True:
        gc.collect()
        # 如果是在非工作时间就暂停任务
        current_timestamp = int(time.time())
        # 如果是每天启动的话就可以不用，也就是一天执行一次，无法执行跨天任务
        if current_timestamp > end_time_stamps[-1] and can_pause:
            scheduler.remove_all_jobs()  # 移除所有任务后，程序执行完成。
            sg.popup_ok("恭喜你完成了今天的所有任务！日志记录在log文件夹对应日期下！输入今天心得吧！")
            # 今日总结
            start_up(config, end=True)
            # 结束后可以玩会游戏
            do_detect_games(config)
            break
        for i in range(len(end_time_stamps)):
            if i > 0:
                if end_time_stamps[i - 1] < current_timestamp < begin_time_stamps[i] and can_pause:
                    pause_schedule(scheduler)
                    # 只有在休息间隔中 才启动休息操作。
                    rest(config, time_span=[end_time_stamps[i - 1], begin_time_stamps[i]])
                    can_pause = False
                elif begin_time_stamps[i] < current_timestamp < end_time_stamps[i] and not can_pause:
                    resume_schedule(scheduler)
                    can_pause = True
            else:
                # 如果比一开始的时间都早就暂停任务，不进行任何操作。
                if current_timestamp < begin_time_stamps[i] and can_pause:
                    pause_schedule(scheduler)
                    can_pause = False
                    print("pause")


if __name__ == '__main__':
    FLAG = True
    main()
