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
1.文章的收藏 delay
2.文章的喜欢或者赞同, 赞同应该不近包括文章,还可以对评论,以及可能的其他对象
3.文章加标签
4.迁移python3
5.迁移使用mysql
6.第三方依赖升级， 已完成
7.消息，如被关注会有消息，被点赞会有消息
8. 重新设计comment，允许回复评论, 滚动到哪个评论才会在哪个评论那里出现回复的入口,参考果库的评论设计，评论的点赞和回复
9. 改版评论,评论应该作为社区的主题予以重视,参考v站的形式,不分父评论和子评论,扁平化,所有评论是平行的平等的,
10, 赞同按钮点击之后变色,再点击恢复,参考果库图文,优先级不高

###Finish
评论扁平排版
评论的点赞

类似知乎的组织方式