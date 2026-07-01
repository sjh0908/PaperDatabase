from database.dao import get_user_by_username, create_user

def init_admin():
    username = "admin"
    password = "admin123"

    existing_user = get_user_by_username(username)

    if existing_user is not None:
        print("管理员账户已存在")
        return

    create_user(
        username=username,
        password=password,
        user_role="admin"
    )

    print("管理员账户创建成功")
    print("用户名：admin")
    print("密码：admin123")


if __name__ == "__main__":
    init_admin()