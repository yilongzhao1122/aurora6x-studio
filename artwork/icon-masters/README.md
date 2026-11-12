# 外部 PNG 母版

本目录只供电脑端生成脚本读取，不属于手表资源路径。保留原始 PNG，不在原图上绘制或覆盖像素。

使用 `tools/icons.json` 中的英文名称保存，例如 `steps.png`、`heart.png`。全部 39 个名称均可导入。当前提供 6 张母版；缺少母版的图标继续使用原绘图定义和固定编号。未知名称会输出警告并忽略。空图会报错。

优先提供透明背景 PNG，脚本以 alpha 为轮廓，忽略 RGB 颜色；不透明黑白图按上下边界推断背景。最终 RGB 全为白色，alpha 只有 0 和 255。不要提交带复杂背景的图片。

`pixel-hints.json` 分别记录 16 和 24 像素的阈值、视觉范围和像素修整。坐标以最终字形左上角为原点；先执行 `set`（置白），再执行 `clear`（透明）。像素修整只在母版 SHA-256 相符时应用，替换母版后不会误用旧轮廓的像素修整。替换图片后应重新查看对比图，再更新对应 SHA 和修整。现有母版的修整包括心形凹口、火苗尖端、闪电轮廓、山峰内部空隙。

16 像素的最大图形范围为 14 像素，四边至少保留 1 像素透明边距；24 像素的最大范围为 20 像素，四边至少保留 2 像素。按有效 alpha 范围等比缩放并居中，两个尺寸分别从母版生成，24 像素不由 16 像素放大。

本次上传的 `sun.png` 实际是“圆环内闪电”，脚本按原图保留图案，并继续对应原来的 sun 编号 14 与相关天气/太阳能字段。

在项目根目录执行：

```powershell
python -X utf8 tools/generate_icons.py
python -X utf8 tools/make_settings_page.py
python -X utf8 tools/check_icon_import.py
```

输出的单独原生图标位于 `artwork/icon-pixels/16/` 和 `artwork/icon-pixels/24/`；设备只使用 `resources/fonts/Icons16.png` 和 `Icons24.png`。
