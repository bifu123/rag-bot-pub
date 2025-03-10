@echo off
REM 设置窗口标题
title ylbot-元龙机器人QQ版
REM 激活环境
call conda activate rag-bot
REM 运行 Python 脚本
python listen_ws.py
