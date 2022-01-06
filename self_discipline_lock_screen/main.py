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


def start_gui(config):
    layout = [
        [sg.Text(config["title"], size=(30, 1), justification='center', text_color="#000", font=("Helvetica", 60))],
        [sg.Text('输入你今天的计划吧！', font=("宋体", 40), text_color="#000")],
        [sg.Multiline(size=(50, 5), key='plan')],

        [sg.Button('确定计划', size=(10, 1), key='set_plan')],
    ]
    top_window = sg.Window('Everything bagel', layout, finalize=True, keep_on_top=True, grab_anywhere=False,
                           transparent_color=sg.theme_background_color(), no_titlebar=True, element_justification='c')
    return top_window


def background_gui(config):
    """
    每次生成一个随机背景的全屏窗口
    """
    x = random.randint(0, len(os.listdir(config["background_pth"])))
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
        window, event, values = sg.read_all_windows(timeout=20)
        print(event, values)
        if event is None or event == 'Cancel' or event == 'Exit':
            print(f'closing window = {window.Title}')
            break
        current_timestamp = int(time.time())
        _, have_face = face_detect()
        if have_face:
            speech(config["reminder_rest"])
        if current_timestamp > time_span[-1]:
            break

    rest_window.close()
    background_window.close()


def start_up(config):
    # 初始化界面
    background_window = background_gui(config)
    lockscreen_window = start_gui(config)
    while True:
        window, event, values = sg.read_all_windows()
        print(event, values)
        if event is None or event == 'Cancel' or event == 'Exit':
            print(f'closing window = {window.Title}')
            break
        if event is "set_plan":
            # 写入计划到md中,就关闭这个启动界面
            if len(values["plan"]) > 0:
                content = config["md_title"] + "### 今日计划\n\n" + values["plan"] + "\n\n"
                with open(config["md_path"], "w", encoding="utf-8") as f:
                    f.write(content)
                break
            else:
                # 没有输入提示
                sg.popup_ok("请输入计划！", keep_on_top=True)
    lockscreen_window.close()
    background_window.close()


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
    # 启动窗口，输入今日计划
    start_up(config)

    # 获取记录的时间，并改为时间戳格式
    begin_time_stamps, end_time_stamps = deal_time(config)
    # 无论如何都先创建一个定时任务，这个定时任务不会立即执行，而是在经过时间间隔后才执行
    scheduler, can_pause = do_schedule(config)  # can pause 是为了任务只停止一次
    # 一直激活程序，当时间到了就暂停任务
    while True:
        # 如果是在非工作时间就暂停任务
        current_timestamp = int(time.time())
        # 若果比最大时间大，就停止任务，但是要一直循环下去，不需要设置rest,但是需要更新时间戳了。
        # 如果是每天启动的话就可以不用，也就是一天执行一次，无法执行跨天任务
        if current_timestamp > end_time_stamps[-1] and can_pause:
            scheduler.remove_all_jobs()  # 移除所有任务后，程序执行完成。
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


if __name__ == '__main__':
    main()
