#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
  课表 → 日历文件（.ics）生成器
  重庆人工智能学院  orangerich229
================================================================

【三步上手】
  1. 用记事本 / VS Code 打开本文件；
  2. 只修改下面「① 学期设置」和「③ 课程列表」两块；
  3. 保存后运行：python3 本文件名.py
     同目录下会生成 .ics 文件，双击或拖进手机日历即可导入。

【换人使用 / 换学期时，通常只改 3 个地方】
  · FIRST_MONDAY   —— 开学第一周的星期一
  · COURSES        —— 课程列表
  · CALENDAR_NAME / OUTPUT_FILE —— 日历名字和输出文件名

【课程怎么写】（复制一份改内容即可）
  {
      "name":     "人工智能概论",     # 课程名（必填）
      "teacher":  "廖老师",           # 老师（可留空 ""）
      "location": "B11栋 301室",      # 地点（可留空 ""）
      "weeks":    "2-17",             # 第几周上课
      "weekday":  "周三",             # 星期几
      "periods":  "5-7",              # 第几节到第几节
  }

  weeks  写法： "5"          只有第 5 周
                "2-17"       第 2 到 17 周（每周都有）
                "1-16/2"     第 1 到 16 周里的单数周
                "6-16/2"     第 6 到 16 周里的双数周
                "5,7,9"      第 5、7、9 周
                "2-8,10-16"  第 2-8 周 + 第 10-16 周

  weekday 写法： 周一 周二 周三 周四 周五 周六 周日
                （也可以写 1~7，1 = 周一）

  periods 写法： "3"          第 3 节
                "5-7"        第 5 到 7 节
                "1-2,5-6"    第 1-2 节 和 第 5-6 节（自动拆成两个日程）
================================================================
"""

import datetime
import hashlib
from pathlib import Path


# ================================================================
#  ① 学期设置（换学期改这里）
# ================================================================

FIRST_MONDAY = "2026-09-07"          # 开学第一周的星期一，格式：年-月-日
CALENDAR_NAME = "2026-2027-1 课表"   # 导入日历后显示的名字
OUTPUT_FILE = "课表.ics"             # 生成的日历文件名
TZ_OFFSET_HOURS = 8                  # 时区（中国 = 8，一般不用改）
REMIND_MINUTES = 10                  # 提前多少分钟提醒，0 = 不提醒


# ================================================================
#  ② 作息时间表（学校改了上下课时间才需要改）
#     格式：第几节: ("开始时间", "结束时间")
# ================================================================

PERIODS = {
    1:  ("09:00", "09:45"),
    2:  ("09:55", "10:40"),
    3:  ("10:50", "11:35"),
    4:  ("11:45", "12:30"),
    5:  ("14:00", "14:45"),
    6:  ("14:55", "15:40"),
    7:  ("15:50", "16:35"),
    8:  ("16:45", "17:30"),
    9:  ("19:00", "19:45"),
    10: ("19:55", "20:40"),
    11: ("20:50", "21:35"),
}


# ================================================================
#  ③ 课程列表（换人 / 换学期主要改这里）
#     想加课就复制一整行大括号，改掉内容就行
# ================================================================

COURSES = [
    # ---------------- 人工智能概论 ----------------
    {"name": "人工智能概论", "teacher": "廖老师",
     "location": "重庆人工智能学院 B11栋 301室",
     "weeks": "2-17", "weekday": "周二", "periods": "5-7"},

    # ---------------- 具身智能与机器人 ----------------
    {"name": "具身智能与机器人", "teacher": "张老师",
     "location": "重庆人工智能学院 B11栋 201室",
     "weeks": "5", "weekday": "周日", "periods": "1-2"},

    {"name": "具身智能与机器人", "teacher": "张老师",
     "location": "重庆人工智能学院 B11栋 201室",
     "weeks": "6-14/2", "weekday": "周日", "periods": "1-3"},

    {"name": "具身智能与机器人", "teacher": "张老师",
     "location": "重庆人工智能学院 B11栋 201室",
     "weeks": "6-14/2", "weekday": "周日", "periods": "5-7"},

    {"name": "具身智能与机器人", "teacher": "张老师",
     "location": "重庆人工智能学院 B11栋 201室",
     "weeks": "16,18", "weekday": "周日", "periods": "1-8"},

    # ---------------- 通用人工智能实践（两学期） ----------------
    {"name": "通用人工智能实践(两学期)", "teacher": "袁老师",
     "location": "重庆人工智能学院 B11栋 301室",
     "weeks": "3", "weekday": "周一", "periods": "5-6"},

    {"name": "通用人工智能实践(两学期)", "teacher": "袁老师",
     "location": "重庆人工智能学院 B11栋 301室",
     "weeks": "3", "weekday": "周二", "periods": "1-2"},

    {"name": "通用人工智能实践(两学期)", "teacher": "袁老师",
     "location": "重庆人工智能学院 B11栋 301室",
     "weeks": "4-16/2", "weekday": "周一", "periods": "5-6"},

    {"name": "通用人工智能实践(两学期)", "teacher": "袁老师",
     "location": "重庆人工智能学院 B11栋 301室",
     "weeks": "4-16/2", "weekday": "周二", "periods": "1-2"},

    # ---------------- 三创理论与实践 ----------------
    {"name": "三创理论与实践", "teacher": "许老师",
     "location": "重庆人工智能学院 B11栋 201室",
     "weeks": "5-17/2,18", "weekday": "周五", "periods": "1-4"},

    # ---------------- 学术英语写作 ----------------
    {"name": "学术英语写作", "teacher": "李老师",
     "location": "重庆人工智能学院 B11栋 301室",
     "weeks": "2-17", "weekday": "周三", "periods": "5-6"},

    # ---------------- 最优化理论与方法 ----------------
    {"name": "最优化理论与方法", "teacher": "沈老师",
     "location": "重庆人工智能学院 B8栋 103室",
     "weeks": "2-17", "weekday": "周四", "periods": "5-6"},

    # ---------------- 自然辩证法 ----------------
    {"name": "自然辩证法", "teacher": "徐老师",
     "location": "重庆人工智能学院 B11栋 101室",
     "weeks": "5-12", "weekday": "周四", "periods": "3-4"},
]


# ================================================================
#  ④ 下面是程序代码，一般不需要修改
# ================================================================

_CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "日": 7, "天": 7}


def parse_date(text):
    """把 '2026-09-07' / '2026/09/07' / '2026.09.07' 都转成 date 对象。"""
    s = str(text).strip().replace("/", "-").replace(".", "-")
    return datetime.date.fromisoformat(s)


def parse_weeks(value):
    """把周次写法解析成有序的周次列表。"""
    if isinstance(value, int):
        return [value]
    if isinstance(value, (list, tuple, range, set)):
        return sorted({int(v) for v in value})

    weeks = set()
    text = str(value).replace("，", ",").replace("－", "-").replace("—", "-")
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        step = 1
        if "/" in part:                     # 支持 "6-16/2" 这种步长写法
            part, step_str = part.split("/", 1)
            step = int(step_str)
        if "-" in part:
            a, b = part.split("-", 1)
            weeks.update(range(int(a), int(b) + 1, step))
        else:
            weeks.add(int(part))

    if not weeks:
        raise ValueError(f"无法识别的周次：{value!r}")
    return sorted(weeks)


def parse_weekday(value):
    """把 '周三' / '星期三' / '3' 都解析成 1~7（1 = 周一）。"""
    if isinstance(value, int):
        if 1 <= value <= 7:
            return value
        raise ValueError(f"星期超出范围：{value!r}（应为 1~7）")

    s = str(value).strip().lower()
    for prefix in ("星期", "周", "礼拜"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break

    if s in _CN_NUM:
        return _CN_NUM[s]
    if s.isdigit() and 1 <= int(s) <= 7:
        return int(s)
    raise ValueError(f"无法识别的星期：{value!r}（请写 周一~周日 或 1~7）")


def parse_periods(value):
    """
    把节次写法解析成若干「连续区间」的列表。
    "5-7"      -> [(5, 7)]
    "1-2,5-6"  -> [(1, 2), (5, 6)]   （中间断开就拆成两个日程）
    """
    if isinstance(value, int):
        nums = [value]
    elif isinstance(value, (list, tuple, range, set)):
        nums = [int(v) for v in value]
    else:
        text = str(value).replace("，", ",").replace("－", "-")
        nums = []
        for part in text.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                nums.extend(range(int(a), int(b) + 1))
            else:
                nums.append(int(part))

    nums = sorted(set(nums))
    if not nums:
        raise ValueError(f"无法识别的节次：{value!r}")

    groups = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
        else:
            groups.append((start, prev))
            start = prev = n
    groups.append((start, prev))
    return groups


def date_from_week(first_monday, week, weekday):
    """算出第 week 周、星期 weekday 对应的日期。"""
    return first_monday + datetime.timedelta(days=(week - 1) * 7 + (weekday - 1))


def minutes_of(hhmm):
    """'09:45' -> 585（分钟数）"""
    h, m = str(hhmm).split(":")
    return int(h) * 60 + int(m)


def format_dt(date, minutes):
    """本地日期+分钟 -> UTC 的 iCalendar 时间字符串（...Z），兼容性最好。"""
    dt = datetime.datetime.combine(date, datetime.time()) + datetime.timedelta(minutes=minutes)
    dt -= datetime.timedelta(hours=TZ_OFFSET_HOURS)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def escape(text):
    """iCalendar 文本转义（逗号、分号、反斜杠、换行）。"""
    return (str(text).replace("\\", "\\\\")
                     .replace(";", "\\;")
                     .replace(",", "\\,")
                     .replace("\r\n", "\\n")
                     .replace("\n", "\\n"))


def build_vevent(course, date, p_start, p_end, now_utc):
    """生成一个 VEVENT 块，返回 (开始时间字符串, 行列表)。"""
    name = course["name"]
    teacher = course.get("teacher", "")
    location = course.get("location", "")

    try:
        start_str = format_dt(date, minutes_of(PERIODS[p_start][0]))
        end_str = format_dt(date, minutes_of(PERIODS[p_end][1]))
    except KeyError as e:
        raise SystemExit(
            f"❌ 课程《{name}》用到了第 {e.args[0]} 节，"
            f"但「作息时间表 PERIODS」里没有定义，请检查配置。"
        )

    uid_src = f"{name}|{location}|{start_str}"
    uid = hashlib.md5(uid_src.encode("utf-8")).hexdigest() + "@course-schedule"

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_utc}",
        f"DTSTART:{start_str}",
        f"DTEND:{end_str}",
        f"SUMMARY:{escape(name)}",
    ]
    if location:
        lines.append(f"LOCATION:{escape(location)}")
    if teacher:
        lines.append(f"DESCRIPTION:{escape('教师：' + teacher)}")

    if REMIND_MINUTES > 0:
        lines += [
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"TRIGGER:-PT{REMIND_MINUTES}M",
            f"DESCRIPTION:{escape('提醒：' + name)}",
            "END:VALARM",
        ]

    lines.append("END:VEVENT")
    return start_str, lines


def main():
    first_monday = parse_date(FIRST_MONDAY)
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    header = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//课表生成器//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-TIMEZONE:Asia/Shanghai",
        f"X-WR-CALNAME:{escape(CALENDAR_NAME)}",
    ]

    events = []
    for course in COURSES:
        if not str(course.get("name", "")).strip():
            continue

        weeks = parse_weeks(course.get("weeks"))
        weekday = parse_weekday(course.get("weekday"))
        groups = parse_periods(course.get("periods"))

        for week in weeks:
            date = date_from_week(first_monday, week, weekday)
            for p_start, p_end in groups:
                start_str, block = build_vevent(course, date, p_start, p_end, now_utc)
                events.append((start_str, block))

    events.sort(key=lambda x: x[0])          # 按时间排序，文件更整洁

    body = []
    for _, block in events:
        body.extend(block)

    ics_text = "\r\n".join(header + body + ["END:VCALENDAR"]) + "\r\n"

    out_path = Path(__file__).resolve().parent / OUTPUT_FILE
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics_text)

    print(f" 已生成：{out_path}")
    print(f"   课程配置 {len(COURSES)} 条 → 共 {len(events)} 个日程")


if __name__ == "__main__":
    main()
