#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令行待办事项列表应用
完整版本：包含内存操作、文件持久化和完善的错误处理

功能特点：
- 添加任务：输入新任务并保存
- 查看任务：显示所有待办事项（带状态）
- 标记完成：将任务状态改为已完成
- 删除任务：移除不需要的任务
- 文件存储：数据保存到文件，重启程序后数据不丢失

技术要点：
- 使用列表存储多个任务
- 使用字典表示单个任务（包含内容和状态）
- 使用json模块序列化和反序列化数据
- 完善的输入验证和错误处理机制
"""

# 导入json模块，用于数据存储和加载
# json是一种轻量级的数据交换格式，类似于Python的字典和列表
import json
import sys

# 数据文件名
DATA_FILE = "todos.txt"

# 定义兼容性输出函数（解决Windows编码问题）
def print_safe(text):
    """安全打印，处理编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果编码错误，移除或使用替代字符
        safe_text = text.encode('gbk', errors='ignore').decode('gbk')
        print(safe_text)


def load_tasks():
    """
    从文件加载任务列表
    就像从笔记本中读取之前记录的内容
    """
    global tasks

    try:
        # 尝试打开文件并读取数据
        # 'r' 表示只读模式
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            # 使用json.load()将文件内容转换为Python对象（列表）
            tasks = json.load(file)

        print_safe(f"[i] 已加载 {len(tasks)} 个任务")

    except FileNotFoundError:
        # 如果文件不存在，创建空列表
        # 就像第一次使用新笔记本，里面是空白的
        print_safe(f"[i] 未找到数据文件 '{DATA_FILE}'，创建新的任务列表")
        tasks = []

    except json.JSONDecodeError:
        # 如果文件格式错误，提示用户
        print_safe(f"[x] 数据文件格式错误，创建新的任务列表")
        tasks = []

    except Exception as e:
        # 处理其他意外错误
        print_safe(f"[!] 加载数据时发生错误: {str(e)}")
        tasks = []


def save_tasks():
    """
    将任务列表保存到文件
    就像把购物清单内容抄写到笔记本上保存
    """
    try:
        # 打开文件用于写入（'w'表示写入模式）
        # encoding='utf-8'确保中文正确存储
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            # 使用json.dump()将Python对象转换为JSON格式并写入文件
            # ensure_ascii=False 保证中文字符正常显示而不是转义
            # indent=2 格式化输出，让文件更易读
            json.dump(tasks, file, ensure_ascii=False, indent=2)

        print_safe(f"[+] 数据已保存到 '{DATA_FILE}'")

    except Exception as e:
        print_safe(f"[x] 保存数据时发生错误: {str(e)}")


# 程序启动时加载任务列表
# 创建全局变量存储所有任务
# 列表就像是一个购物清单，可以存放多个项目
tasks = []


def add_task():
    """
    添加新任务
    就像往购物清单上写新物品一样
    """
    print_safe("\n" + "="*30)
    print_safe("添加新任务")
    print_safe("="*30)

    task_content = input("请输入任务内容: ")

    # 检查输入是否为空
    if task_content.strip() == "":
        print_safe("[x] 任务内容不能为空!")
        return

    # 创建任务字典，包含任务内容和完成状态
    # 字典就像是一个带标签的文件夹，可以存储多个相关信息
    new_task = {
        "task": task_content,  # 任务描述
        "done": False          # 完成状态，False表示未完成
    }

    # 将新任务添加到列表中
    # append()方法就像是在清单末尾添加新项目
    tasks.append(new_task)

    print_safe(f"[+] 任务已添加: {task_content}")

    # 自动保存数据到文件
    save_tasks()


def view_tasks():
    """
    查看所有任务
    就像查看购物清单上的所有物品
    """
    print_safe("\n" + "="*30)
    print_safe("待办事项列表")
    print_safe("="*30)

    # 检查列表是否为空
    if len(tasks) == 0:
        print_safe("[i] 暂无任务，请先添加任务!")
        return

    # 遍历列表中的所有任务
    # enumerate()函数可以同时获取索引和元素，就像给清单编号
    for index, task in enumerate(tasks):
        # 根据完成状态显示不同的图标
        status = "[+]" if task["done"] else "[ ]"

        # 显示任务编号、状态和描述
        print_safe(f"{index + 1}. {status} {task['task']}")

    print_safe("="*30)
    print_safe(f"总计: {len(tasks)} 个任务")

    # 计算已完成和未完成的任务数
    completed_count = sum(1 for task in tasks if task["done"])
    pending_count = len(tasks) - completed_count
    print_safe(f"已完成: {completed_count} | 待完成: {pending_count}")


def mark_task_done():
    """
    标记任务为完成状态
    就像在购物清单上打勾表示已购买
    """
    print_safe("\n" + "="*30)
    print_safe("标记任务完成")
    print_safe("="*30)

    # 先检查是否有任务
    if len(tasks) == 0:
        print_safe("[i] 暂无任务可以标记!")
        return

    # 显示所有任务供用户选择
    view_tasks()

    try:
        # 获取用户输入的任务编号
        task_number = input("\n请输入要标记完成的任务编号 (输入0取消): ").strip()

        # 检查是否取消操作
        if task_number == "0":
            print_safe("操作已取消!")
            return

        # 将字符串转换为整数
        task_number = int(task_number)

        # 验证编号是否有效
        # 检查编号是否在有效范围内（1到任务总数）
        if task_number < 1 or task_number > len(tasks):
            print_safe(f"[x] 无效编号! 请输入1到{len(tasks)}之间的数字")
            return

        # 获取实际索引（列表索引从0开始，用户输入从1开始）
        index = task_number - 1

        # 检查任务是否已完成
        if tasks[index]["done"]:
            print_safe(f"[!] 该任务已完成: {tasks[index]['task']}")
        else:
            # 标记为完成
            tasks[index]["done"] = True
            print_safe(f"[+] 任务已完成: {tasks[index]['task']}")

            # 自动保存数据到文件
            save_tasks()

    except ValueError:
        # 处理非数字输入
        print_safe("[x] 请输入有效的数字!")
    except Exception as e:
        # 捕获其他意外错误
        print_safe(f"[x] 发生错误: {str(e)}")


def delete_task():
    """
    删除任务
    就像从购物清单上划掉不需要的物品
    """
    print_safe("\n" + "="*30)
    print_safe("删除任务")
    print_safe("="*30)

    # 先检查是否有任务
    if len(tasks) == 0:
        print_safe("[i] 暂无任务可以删除!")
        return

    # 显示所有任务供用户选择
    view_tasks()

    try:
        # 获取用户输入的任务编号
        task_number = input("\n请输入要删除的任务编号 (输入0取消): ").strip()

        # 检查是否取消操作
        if task_number == "0":
            print_safe("操作已取消!")
            return

        # 将字符串转换为整数
        task_number = int(task_number)

        # 验证编号是否有效
        if task_number < 1 or task_number > len(tasks):
            print_safe(f"[x] 无效编号! 请输入1到{len(tasks)}之间的数字")
            return

        # 获取实际索引
        index = task_number - 1

        # 确认删除操作
        task_content = tasks[index]["task"]
        confirm = input(f"\n[!] 确定要删除任务 '{task_content}' 吗? (y/n): ").lower()

        if confirm == 'y':
            # 删除任务
            deleted_task = tasks.pop(index)  # pop()方法移除并返回指定位置的元素
            print_safe(f"[-] 任务已删除: {deleted_task['task']}")

            # 自动保存数据到文件
            save_tasks()
        else:
            print_safe("操作已取消!")

    except ValueError:
        print_safe("[x] 请输入有效的数字!")
    except Exception as e:
        print_safe(f"[x] 发生错误: {str(e)}")


def main():
    """
    主程序入口
    使用循环持续运行程序，直到用户选择退出
    """
    print_safe("="*45)
    print_safe("[todo] 命令行待办事项列表")
    print_safe("="*45)
    print_safe("数据已启用文件存储，重启程序后数据不会丢失!")

    # 程序启动时加载任务数据
    load_tasks()

    # 主循环，就像自动门持续检测是否有人靠近
    while True:
        print_safe("\n" + "-"*40)
        print_safe("请选择操作:")
        print_safe("1. 添加任务")
        print_safe("2. 查看任务")
        print_safe("3. 标记任务完成")
        print_safe("4. 删除任务")
        print_safe("5. 退出程序")
        print_safe("-"*40)

        choice = input("请输入选项 (1-5): ")

        # 条件判断，根据用户选择执行不同操作
        # 就像交通信号灯指挥交通流向
        if choice == "1":
            # 添加任务
            add_task()

        elif choice == "2":
            # 查看任务
            view_tasks()

        elif choice == "3":
            # 标记任务完成
            mark_task_done()

        elif choice == "4":
            # 删除任务
            delete_task()

        elif choice == "5":
            # 退出程序（带确认）
            if exit_program():
                break

        else:
            # 无效输入
            print_safe("[x] 无效选项，请输入1-5之间的数字")


def exit_program():
    """
    退出程序前的确认
    """
    print_safe("\n" + "="*35)
    confirm = input("确定要退出程序吗? (y/n): ").lower()
    if confirm == 'y':
        print_safe("[bye] 感谢使用，再见!")
        return True
    return False


# 程序入口
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # 处理 Ctrl+C 中断
        print_safe("\n\n[!] 程序被中断")
    except Exception as e:
        # 捕获任何未处理的异常
        print_safe(f"\n[x] 发生未预期的错误: {str(e)}")
        print_safe("请检查错误信息并尝试重新运行程序!")
