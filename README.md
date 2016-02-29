# flask-demo
个人Flask练手项目，以pycon2014上miguel的项目为基础进行改编,实现了一个简易的
微博客,具有注册、登录、发博客、关注、评论等功能.
###使用说明

1. git clone https://github.com/goalong/flask-demo.git
2. cd flask-demo
3. virtualenv venv
4. source venv/bin/activate
5. pip install -r requirements.txt
6. python manage.py runserver
7. 打开浏览器，在地址栏输入http://localhost:5000/
8. 注册用户，在终端输入 python manage.py adduser <email> <username> 

###Todo
1.收藏
2.喜欢或者赞同
3.扩展账号系统,支持手机号以及第三方登录