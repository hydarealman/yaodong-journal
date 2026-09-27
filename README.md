# Yaodong’s Journal

个人博客：[访问网站](https://hydarealman.github.io/yaodong-journal/)。使用 Hugo + PaperMod 构建。

## 内容维护

当前唯一内容来源：`D:\技术文档`。保留原始 Markdown 标题层级与文件夹，不修改源文件。

```powershell
cd D:\yaodong-journal
python scripts/import_curated.py
hugo server
```

导入会在项目同级目录创建备份，再同步替换 `content/posts`，复制图片与附件、修复链接，并生成 `import-report.json`。已从源目录移除的文章不会保留在新站中。飞书临时授权图片若未导出为本地文件，会显示待补充提示。

分类映射在 `data/journal_index.json`，五个篇章的定义在 `data/journal_topics.json`。

文章目录覆盖 Markdown 1–6 级标题，支持点击定位、分支折叠、全部展开/折叠、滚动高亮。桌面为固定侧栏，手机为可展开目录。

## 发布

提交并推送到 main 后，GitHub Actions 构建 Hugo、生成 Pagefind 搜索索引并部署 GitHub Pages。

本次内容替换前的完整备份位于 `D:\blog-content-backup-20260927`，包含原先未提交的文章修改与旧媒体。
