@echo off
REM 设置窗口标题
title 测试
REM 激活环境
call conda activate rag-bot
REM 运行 Python 脚本
python test.py

pause
