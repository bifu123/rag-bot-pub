from sqlite_helper import *
from send import *
# 异步函数
import asyncio
import aiohttp


def do_custom_command(command_name, source_id, user_id, user_state, command_main, chat_type, group_id, at):
    command_main = command_main[0]
    command_id = command_main[0]
    pamas_num = command_main[2]
    command_code = command_main[3]
    print(command_id, pamas_num, command_code)
    
    drop_current_command_table(command_name, user_id, source_id, user_state) # 删除表
    copy_params_for_command(command_name, user_id, source_id, user_state) # 复制到当前用户命令表
    
    # 获得用户当前自定义命令
    q = fetch_user_current_command(command_name, user_id, source_id, user_state)
    
    # 发送消息
    response_message = q[3]
    asyncio.run(answer_action(chat_type, user_id, group_id, at, response_message))
    
    # 锁定用户
    switch_user_lock(user_id, source_id, user_state, 1)

def update_custom_command(get_value, source_id, user_id, user_state, chat_type, group_id, at):
    table_name = f"current_command_{user_id}_{source_id}"
    # 获取命令的参数数量
    sql = f'''SELECT params_num FROM command_main 
               WHERE command_name = (SELECT command_name FROM {table_name} 
               WHERE user_id = "{user_id}" 
               AND source_id = "{source_id}"
               AND user_state = "{user_state}")'''
    params_num = select_handler_one(sql)[0]
    print("当前命令参数数量：", params_num)
    user_receive_param_num = get_user_receive_param_num(user_id, source_id, user_state)
    print("当前己接收的参数数量：", user_receive_param_num)

    
    if user_receive_param_num < params_num:
        # 更新最小ID为空参数的值
        sq2 = f'''UPDATE {table_name} SET get_value = "{get_value}", user_state = "{user_state}"
                WHERE id = (SELECT id FROM {table_name} WHERE user_id = "{user_id}"
                            AND source_id = "{source_id}"
                            AND (get_value = "" OR get_value IS NULL)
                            AND user_state = "{user_state}"
                            ORDER BY id ASC
                            LIMIT 1
                            )'''
                            
        command_handler(sq2)
        print(f"自定义命令参数 {user_receive_param_num} 更新完成")
        
        
        # 获取当前命令值为空的最小记录
        sql1 = f'''SELECT keyword, param_name FROM {table_name} 
                        WHERE id = (SELECT MIN(id) FROM {table_name} WHERE user_id = "{user_id}"
                        AND source_id = "{source_id}"
                        AND (get_value = "" OR get_value IS NULL)
                        AND user_state = "{user_state}"
                        LIMIT 1
                        )'''
        try:
            q1 = select_handler_one(sql1)
            keyword, param_name = q1[0], q1[1]
        except:
            keyword, param_name = None, None
        print(f"keyword:{keyword}")
        
        if keyword is not None:
            asyncio.run(answer_action(chat_type, user_id, group_id, at, keyword))
        else:
            # 执行命令
            print("所有参数收集完成，执行命令")
            # 获取当前命令值
            sql2 = f'''SELECT a.command_name, a.param_name, a.get_value, b.command_code FROM {table_name} a left join command_main b on a.command_name = b.command_name 
                        WHERE a.user_id = "{user_id}"
                        AND a.source_id = "{source_id}"
                        AND a.user_state = "{user_state}"'''
            rows = select_handler_all(sql2)


            command_code = rows[0][3] # print(f'你的姓名是：{p1_value}{p2_value}')

            for i in range(1, len(rows)+1):
                param_key = "{{p{}_value}}".format(i)
                command_code = command_code.replace(f"{param_key}", f"{rows[i-1][2]}")

            print(f"命令代码：{command_code}")     

            exec(command_code) 
            # 解锁用户
            switch_user_lock(user_id, source_id, user_state, 0)   
            print(f"己解锁用户: {user_id}")
    else:
        switch_user_lock(user_id, source_id, user_state, 0)
            

           
        