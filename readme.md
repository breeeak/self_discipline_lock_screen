# Self_discipline_lock_screen

## 一款帮助自律的桌面程序

适合于需要长时间在电脑屏幕前进行工作的人。类似于番茄钟，帮助自律，卷就完了:trollface: 。

![项目](./self_discipline_lock_screen/2022-01-06_161607.jpg)

### 主要功能

1. 启动时可以设定今日计划。
2. 定义工作时间与休息时间，工作时间会截取电脑屏幕和开启摄像头抓拍检测人脸作为图像记录，休息时会锁定屏幕，并检测人脸，提醒出去活动。
3. 生成md文档，记录一天的状态。

### 安装与使用

该软件基于python(>=3.6)，目前在Windows系统(Win10)上测试通过。

1. 直接从github下载文件或者git clone此项目。

2. 安装依赖，建议可以新建一个虚拟环境。
```
pip install -r requirements.txt
# 如果dlib包安装失败，可以直接使用model中的whl文件安装
pip install ./model/dlib-19.8.1-cp36-cp36m-win_amd64.whl
```
> 主要的使用的包有pysimplegui,opencv,APScheduler

3. 设置一下计划
   1. title: 程序名称，可改为激励自己的名言。
   2. time_intervals: 工作时间定义，小时：分钟：秒。一行为一个工作时间段，两个工作时间段之间为休息时间，请按照规则来设定
   3. reminder: 提醒工作的提示语，可以语音播报。
   4. reminder_rest: 提醒休息的提示语，可以语音播报。
   5. interval: 多少分钟抓拍一次摄像头，记录工作状态。
```json
{
  "title":"自律人生",
  "time_intervals": [
    ["08:30:00","09:00:00"],
    ["15:20:00","15:25:00"],
    ["15:36:00","15:55:00"]
  ],
  "reminder": "抓紧来学习啦！",
  "reminder_rest": "离开座位,出去休息一下吧!",
  "interval": 5
}


```
> 这里设定的是一天的计划，不能跨天，第二天需要重新启动程序
> 不是真正的锁屏，是置顶gui。自律还是要靠自己

4. 对于windows系统，可以将start.bat，建立快捷方式，添加到你的开机启动文件夹`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`中，实现开机启动。
> start.bat 里面的内容需要按自己的路径修改。

### TODO
1. 生成release安装包
2. 多屏幕，更好的自定义计划等
3. 优化代码，内存增加问题

### 说明
代码有比较详细的注释，由于本人科研任务繁重，暂时不会更新，如果感兴趣可以提交request，欢迎star。
