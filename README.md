# Parcel Locker System — Streamlit

基于原有 Parcel、Locker、Recipient 和 ParcelLockerSystem 的网页版本。
保留 CLI：`python main.py`。网页入口：`app.py`。

## 启动

建议 Python 3.11 或更新版本；已在 Python 3.14 / Streamlit 1.65.0 验证。
在此项目文件夹打开终端：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

也可双击 `Start-Streamlit.cmd`，首次运行会创建独立环境并安装依赖，需要联网。
终端保持开启，浏览器访问 http://localhost:8501；停止时在终端按 Ctrl+C。

## 页面

- Home：功能入口。
- Register Parcel：填写姓名、联系方式、快递单号，自动分配空柜并生成六位取件码。
- Collect Parcel：先验证取件码，再确认取件；确认后释放柜子。
- Parcel Records：实际保存的记录，不预填效果图中的虚构数据。
- Locker Status：12 个柜子，桌面四列、窄屏两列，灰色表示占用。

样式对应所提供的四张效果图：白底、深色文字、蓝色按钮、细边框，并增加左侧导航。
成功内容仅在成功操作后显示。错误码、已取件、柜满、空字段和重复单号会给出提示。

## 数据与边界

第一次启动没有 data.json 时，会显示 12 个空柜。首次登记后自动创建文件。
数据文件保存包裹与柜子状态，兼容原版 JSON；修改前请备份此文件。
读写错误时显示错误，不会用空数据覆盖无法读取的文件。
写入使用临时文件和原子替换；同一 Streamlit 进程内的会话操作串行处理。
不要用多个服务进程或 CLI 同时写同一数据文件。后续公开、多实例部署应改用数据库事务。
在临时文件系统的云平台上，JSON 不保证长期保存；此版本定位为本机课程演示。

Courier / Customer / Staff 是页面角色标签，并非登录或权限验证。
所有演示页面可通过导航访问，不适合直接公开真实个人信息。
开柜是模拟操作，通知只是预览，没有发送短信或邮件。

## MVC 分工

- `parcel.py`、`locker.py`、`recipient.py`：原有实体模型及规则。
- `system.py`：业务服务，分配柜位、生成代码、处理取件。
- `controller.py`：协调页面操作，读取最新状态并串行处理变更。
- `repository.py`：JSON 读取与安全写入。
- `views.py`、`styles.css`：Streamlit 页面和样式。
- `app.py`：网页启动入口。`main.py`：保留的 CLI 入口。

## 验证

```powershell
.\.venv\Scripts\python.exe -m unittest test_app.py -v
```

测试使用临时文件，不修改真实 data.json。覆盖完整登记/取件、重启恢复、重复单号、
柜满、重复取件、多个会话、损坏数据、写入失败，以及 Streamlit 页面交互。

Streamlit 官方文档：https://docs.streamlit.io/develop
