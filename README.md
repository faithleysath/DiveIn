# DiveIn

DiveIn 是一个基于 FastAPI 和 Python 的轻量级爬虫框架，旨在简化爬虫开发过程。当前版本展示了如何爬取百度贴吧的数据，并通过前端页面进行展示。

## 特性

- **灵活的适配器机制**：可以轻松扩展以支持不同的网站和 API。
- **基于 FastAPI**：提供高性能的异步接口。
- **模块化设计**：清晰的目录结构，便于维护和扩展。

## 安装

你可以使用 pip 来安装 DiveIn：

```bash
pip install divein
```

## 使用方法

### 运行爬虫

首先，确保你已经安装了所需的依赖。你可以使用以下命令来安装依赖：

```bash
pip install -r requirements.txt
```

然后运行主程序：

```bash
python main.py
```

### 访问前端页面

运行主程序后，打开浏览器并访问 `http://localhost:8000`。你将看到爬取到的百度贴吧数据展示在前端页面中。

## 目录结构

项目的主要目录结构如下：

- `main.py`：主程序入口
- `adapters/`：适配器目录，包含百度贴吧的爬虫实现
- `cookies/`：存储 cookies
- `models/`：数据模型
- `static/`：前端静态文件
- `utils/`：工具函数

## 贡献

欢迎提交 issue 和 pull request 来帮助改进 DiveIn。

## 许可证

DiveIn 遵循 [GNU Affero General Public License (AGPL)](https://www.gnu.org/licenses/agpl-3.0.html) 许可证。该许可证要求所有基于该代码的修改和衍生作品也必须开源，并且在网络服务下使用时也需要开源。如果你希望将 DiveIn 用于商业用途，请联系原作者获取授权。

## 联系方式

如果你有任何问题或建议，请随时通过 [GitHub Issues](https://github.com/你的用户名/DiveIn/issues) 与我们联系。
