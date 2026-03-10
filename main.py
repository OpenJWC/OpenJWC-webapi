from fastapi import FastAPI

# 1. 实例化 FastAPI 对象
app = FastAPI()


# 2. 定义一个路由（路由就是 URL 路径，比如 / 或 /hello）
# 当有人通过 GET 方法访问你的根目录时，执行这个函数
@app.get("/")
def read_root():
    return {"message": "Hello, 教务处助手后端已启动!"}


# 3. 定义一个带参数的路由
# 如果用户访问 /info/1，这里会把 item_id 作为参数传进去
@app.get("/info/{item_id}")
def read_item(item_id: int):
    return {
        "item_id": item_id,
        "status": "success",
        "detail": "这是来自服务器的通知详情。",
    }
