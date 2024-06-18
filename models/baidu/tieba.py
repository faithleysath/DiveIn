from peewee import (
    Model,
    SqliteDatabase,
    IntegerField,
    CharField,
    FloatField,
    BooleanField,
    DateTimeField,
    ForeignKeyField,
    TextField,
)
import datetime

# 配置数据库路径
DATABASE_PATH = "tiebaDB.db"


# 基础模型类，定义数据库连接信息
class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(DATABASE_PATH)


# 用户模型
class User(BaseModel):
    user_id = IntegerField(primary_key=True)  # 用户ID，主键
    user_name = CharField(null=True)  # 用户名，可以为空
    portrait = CharField(unique=True)  # 用户画像，唯一
    user_nickname = CharField(null=True)  # 用户昵称，可以为空
    show_nickname = CharField(null=True)  # 显示的昵称，可以为空
    age = FloatField(null=True)  # 用户年龄，可以为空，单位为年
    sex = CharField(null=True)  # 用户性别，可以为空
    followed_count = IntegerField(default=0)  # 被关注数
    post_num = IntegerField(null=True)  # 发帖数
    is_vip = BooleanField(null=True)  # 是否为贴吧会员
    is_block = BooleanField(null=True)  # 是否被封
    is_private = BooleanField(null=True)  # 是否私密
    ip_location = CharField(null=True)  # ip属地
    updated_at = DateTimeField(default=datetime.datetime.now)  # 数据库记录更新时间


# 论坛模型
class Forum(BaseModel):
    forum_id = IntegerField(primary_key=True)  # 论坛ID，主键
    forum_name = CharField()  # 论坛名称
    first_class = CharField(null=True)  # 一级分类
    second_class = CharField(null=True)  # 二级分类
    followed_count = IntegerField(null=True)  # 关注数
    thread_num = IntegerField(null=True)  # 贴子数
    post_num = IntegerField(null=True) # 楼层数
    updated_at = DateTimeField(default=datetime.datetime.now)  # 数据库记录更新时间


# 贴子模型
class Thread(BaseModel):
    thread_id = IntegerField(primary_key=True)  # 贴子ID，主键
    thread_title = CharField()  # 贴子标题
    author = ForeignKeyField(
        User, backref="threads", null=True
    )  # 贴子的作者，外键关联用户
    forum = ForeignKeyField(
        Forum, backref="threads", null=True
    )  # 贴子所属贴吧，外键关联论坛
    content = TextField()  # 贴子内容
    is_deleted = BooleanField(default=False)  # 是否删除，默认值为False
    created_at = DateTimeField(null=True)  # 创建时间
    ip_location = CharField(null=True)  # ip属地
    thread_from = CharField(null=True)  # 贴子来源
    updated_at = DateTimeField(default=datetime.datetime.now)  # 数据库记录更新时间


# 楼层模型
class Post(BaseModel):
    post_id = IntegerField(primary_key=True)  # 楼层ID，主键
    floor = IntegerField()  # 楼层数
    author = ForeignKeyField(
        User, backref="posts", null=True
    )  # 楼层的作者，外键关联用户
    content = TextField()  # 楼层内容
    thread = ForeignKeyField(
        Thread, backref="posts", null=True
    )  # 所属贴子，外键关联贴子
    forum = ForeignKeyField(
        Forum, backref="threads", null=True
    )  # 楼层所属贴吧，外键关联论坛
    comment_num = IntegerField(default=0)  # 评论数，默认值为0
    is_anonym = BooleanField(default=False)  # 是否匿名，默认值为False
    is_fold = BooleanField(default=False)  # 是否折叠，默认值为False
    is_deleted = BooleanField(default=False)  # 是否删除，默认值为False
    post_time = DateTimeField(default=datetime.datetime.now)  # 发表时间，默认当前时间
    ip_location = CharField(null=True)  # ip属地
    post_from = CharField(null=True)  # 贴子来源
    updated_at = DateTimeField(default=datetime.datetime.now)  # 数据库记录更新时间


# 评论模型
class Comment(BaseModel):
    comment_id = IntegerField(primary_key=True)  # 评论ID，主键
    post = ForeignKeyField(
        Post, backref="comments", null=True
    )  # 所属楼层，外键关联楼层
    thread = ForeignKeyField(
        Thread, backref="posts", null=True
    )  # 所属贴子，外键关联贴子
    author = ForeignKeyField(
        User, backref="comments", null=True
    )  # 评论的作者，外键关联用户
    content = TextField()  # 评论内容
    is_deleted = BooleanField(default=False)  # 是否删除，默认值为False
    comment_from = CharField(null=True)  # 评论来源
    comment_time = DateTimeField(
        default=datetime.datetime.now
    )  # 评论时间，默认当前时间
    location = TextField(null=True)  # 经纬度、位置的json数据
    updated_at = DateTimeField(default=datetime.datetime.now)  # 数据库记录更新时间


# 用户论坛模型
class UserForum(BaseModel):
    user = ForeignKeyField(User, backref="user_forums")  # 用户，外键关联用户
    forum = ForeignKeyField(Forum, backref="user_forums")  # 论坛，外键关联论坛
    user_level = IntegerField(null=True)  # 用户等级，可以为空
    user_exp = IntegerField()  # 用户经验值
    is_like = BooleanField()  # 是否喜欢
    favo_type = IntegerField()  # 收藏类型
    created_at = DateTimeField(default=datetime.datetime.now)  # 创建时间，默认当前时间
    updated_at = DateTimeField(default=datetime.datetime.now)  # 数据库记录更新时间


# 创建数据库表
database = SqliteDatabase(DATABASE_PATH)
database.create_tables([User, Forum, Thread, Post, Comment, UserForum])
