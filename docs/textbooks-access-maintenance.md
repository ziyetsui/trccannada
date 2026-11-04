# 教材学习室加密版维护

部署来源仍为 `publish/website` 分支根目录，网址不变。`learning-library/textbooks/`只发布加密后的`index.html`和图片，不发布课程JSON、逐课Markdown、插图文字清单、模板及原构建器。

## 更新课程或访问码

1. 在仓库外的私人源目录编辑课程，执行原`learning-library/textbooks/build.py`。不要将明文源目录放进公开仓库或提交历史。
2. 在本仓库执行`npm ci`安装锁定的StatiCrypt。
3. 安全地设置环境变量`STATICRYPT_PASSWORD`，再执行`python3 scripts/protect_textbooks.py --source /absolute/private/site/learning-library/textbooks`。访问码至少16字符，应使用随机长码。
4. 运行`npm test`；再执行`python3 tests/check_textbooks_access.py --password-file /absolute/private/access-code.txt`，检查真正的289课加密版本。需要跑原明文构建器和浏览器套件时，设置`TEXTBOOK_TEST_ROOT=/absolute/private/site`再运行`npm test`。
5. 确认Git差异只含密文和必要图片后提交部署。线上复验：`python3 tests/check_textbooks_access.py --url https://ziyetsui.github.io/trccannada/learning-library/textbooks/ --password-file /absolute/private/access-code.txt`。

CLI从环境变量读取访问码，不接受维护脚本的密码参数。密码文件、`.env`及`node_modules`不提交。`scripts/textbooks-access-salt.json`为公开的随机盐，保留它可使记住设备在同一码的后续内容更新中继续有效；它不是密码。修改访问码后重新加密即可，旧记忆不能解开新内容，但已下载副本无法撤回。

发布脚本会拒绝仓库内部来源、过短码和重叠目录，先完成加密与图片筛选，再替换发布目录；准备失败时保留原发布物。来源页须先构建为内嵌数据和脚本的HTML。退出只清理`textbooks.access.*`，不清理学习进度与主题。

## 保护边界

这是浏览器端加密，密文公开可下载，不能可靠限制离线猜码、转发或已授权者保存内容。不要使用短数字码。只保护新的发布入口；以前的公开提交、其他分支和第三方缓存仍可能有课程副本。本次未改写历史，也未变更仓库可见性。

插图保留原公开静态路径；原有230课学习库和TCF页面继续公开。
