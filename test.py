'''
遍历若干个python函数，每个函数返回的值都作为下一个函数的参数，求最后一个返回的结果
'''

def func1():
    return 10

def func2(x):
    return x * 2

def func3(x):
    return x + 5

def func4(x):
    return x - 3

# 定义函数列表
functions = [func1, func2, func3, func4]

# 初始化参数为 None
result = None

# 遍历函数列表
for func in functions:
    if result is None:
        # 对于第一个函数，参数为 None
        result = func()
    else:
        # 对于其他函数，参数为上一个函数的返回值
        result = func(result)

# 最后一个函数的返回值即为结果
print("最终结果:", result)

'''
这段代码定义了四个函数，然后将它们放入一个列表中。然后通过循环遍历列表中的每个函数，每次迭代时将上一个函数的返回值作为参数传递给当前函数，并更新结果。最后打印出最终结果。
'''
