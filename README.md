环境：
Python 3.14.5
MySQL 8.0.45

进入虚拟环境（Windows）：
在项目根目录下：Bash：python -m venv .venv 
Powershell：.venv\Scripts\Activate.ps1或cmd：.venv\Scripts\activate

安装（恢复环境）：
pip install -r requirements.txt

创建.env：
Bash：copy .env.example .env
进入.env修改MYSQL_PASSWORD为自己的MySQL密码，修改SECRET_KEY为随机字符串

初始化数据库：
mysql>SOURCE database/schema.sql

初始化管理员账号：
Bash：python init_admin.py
默认账号：admin；默认密码：admin123

运行：
Bash：python app.py

访问：
浏览器：http://127.0.0.1:5000

退出：
Bash：Ctrl + C