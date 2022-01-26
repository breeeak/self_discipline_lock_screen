# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 11:05
# @Author  : Marshall
# @FileName: pyauto.py
# 一个自动化的程序，可以记录鼠标键盘操作，然后执行自动化操作，TODO 很多功能都有待完善，目前只可以进行简单的记录点击等，有很多bug,可以参考按键精灵，与之不同的是，做的是图片匹配，而不是简单的坐标（目前还没完成）
import pyautogui as pag
import PySimpleGUI as sg
import pynput.keyboard as pk
import pynput.mouse as pm
import threading
import time
import os


def on_press(key):
    # 停止标志
    if str(key) == r"<48>":  # ctrl 0
        global STOP_FLAG
        STOP_FLAG = True
        return False
    # 监听按键
    print(str(key))
    global CONFIG
    path = os.path.join(CONFIG["SAVE_PATH"], "KEY_EVENT.txt")
    with open(path, "a+", encoding="utf-8") as f:
        f.write(str(CONFIG["STEP"]) + ":key:" + str(key) + ":" + str(int(time.time())) + ":" + "None" + "\n")
    CONFIG["STEP"] = CONFIG["STEP"] + 1




def on_scroll(x, y, dx, dy):
    # 停止标志
    global STOP_FLAG
    if STOP_FLAG:
        return False
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))


def on_click(x, y, button, pressed):
    # 停止标志
    global STOP_FLAG
    if STOP_FLAG:
        return False
    # 监听鼠标点击
    if pressed:
        global CONFIG
        print("按下坐标")
        w_ = CONFIG["W"]
        h_ = CONFIG["H"]
        x_ = x - int(w_ / 2)
        y_ = y - int(h_ / 2)
        if x_ < 0:
            x_ = 0
        if y_ < 0:
            y_ = 0
        if x_ + w_ > CONFIG["SCREEN_W"]:
            x_ = CONFIG["SCREEN_W"] - w_
        if y_ + h_ > CONFIG["SCREEN_H"]:
            y_ = CONFIG["SCREEN_H"] - h_
        img_step = pag.screenshot(region=(x_, y_, w_, h_))
        img_pth = os.path.join(CONFIG["SAVE_PATH"], "STEP_" + str(CONFIG["STEP"]) + ".png")
        img_step.save(img_pth)
        key_path = os.path.join(CONFIG["SAVE_PATH"], "KEY_EVENT.txt")
        mxy = "{},{}".format(x_, y_)
        with open(key_path, "a+", encoding="utf-8") as f:
            f.write(str(CONFIG["STEP"]) + ":"+str(button)+":" + mxy + ":" + str(int(time.time())) + ":" + str(img_pth) + "\n")
        CONFIG["STEP"] = CONFIG["STEP"] + 1


        print(mxy)


def ls_k_thread():
    global STOP_FLAG
    while not STOP_FLAG:
        with pk.Listener(on_press=on_press) as pklistener:
            pklistener.join()


def ls_m_thread():
    global STOP_FLAG
    while not STOP_FLAG:
        print(STOP_FLAG)
        with pm.Listener(on_click=on_click, on_scroll=on_scroll) as pmlistener:
            pmlistener.join()


def analyse_pic_thread():
    result = sg.popup_ok("按下下方【确定键】开始录制，按下组合键【Ctrl+0】结束录制")
    if result == "OK":
        global CONFIG
        CONFIG["SAVE_PATH"] = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(int(time.time())))
        os.makedirs(CONFIG["SAVE_PATH"])
        k_thread = threading.Thread(target=ls_k_thread)
        k_thread.start()
        m_thread = threading.Thread(target=ls_m_thread)
        m_thread.start()


def do_job(path):
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
        if i == 0:
            time.sleep(15)
        else:
            time.sleep(2)
    print(key_event)


if __name__ == '__main__':
    # STOP_FLAG = False
    # FLAG = True     # 发送消息的Flag
    # screenWidth, screenHeight = pag.size()
    # SAVE_PATH = ""
    # STEP = 0
    # W = 40
    # H = 40
    # CONFIG = {"SAVE_PATH": SAVE_PATH, "SCREEN_W": screenWidth, "SCREEN_H": screenHeight, "STEP": STEP, "W": W, "H": H}
    # analyse_pic_thread()
    # print(1)
    FLAG = True
    do_job("2022-01-26-16-16-53")
