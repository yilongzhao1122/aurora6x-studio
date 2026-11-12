# Development and resource maintenance

Source is in `source/`, runtime resources in `resources/`, and artwork masters/font sources with licenses in `artwork/`. Windows build entry points call `tools/Build.ps1`. Normal builds use generated resources.

Install Python 3.12+ and dependencies when regenerating artwork:

```sh
python -m pip install -r tools/requirements-artwork.txt
python tools/generate_onwatch.py
python tools/generate_icons.py
python tools/make_settings_page.py
```

`tools/typography.py` defines rasterization. Small is 14px, SmallPlus is 16px, ordinary data digit ink height is 20px, C1 digit ink height is 22px, main-clock digit ink height is 58px and seconds are 33px. Digit height is normalized by cap height, so changing only the nominal size or FNT header will not resize the visible digits. Font declarations, loading and release are in `source/AuroraView.mc`. Keep low-memory graphics release handling when adding fonts.

Run the local checks documented in the workflow or [Chinese development notes](开发说明.md). These use source/API/DOM doubles and real bitmap pixels; they do not replace official simulator or watch testing.

After committing the intended files, run `python release/package_source.py`. It creates reproducible CN and EN source ZIPs plus `dist/SHA256SUMS.txt`, including only committed files. Both packages support both languages; only the starting language and its preview configuration differ.

For maintainers, run `release/Publish.ps1` with an already authenticated GitHub CLI, or create a matching GitHub Release in the web UI and upload both ZIPs plus `SHA256SUMS.txt`. Use `RELEASE_NOTES.md` for the bilingual description. The project does not install a privileged publishing workflow.
