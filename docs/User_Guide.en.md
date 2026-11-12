# Installation, preview and on-watch settings

[中文](使用说明.md) · [Home](../README.en.md)

## Prepare your computer

Install Java, VS Code, Garmin Monkey C and Connect IQ SDK. Download the official `fenix6xpro` device package in SDK Manager. Generate your own developer key using Monkey C and place the key FILE at `keys/developer_key`. Alternatively set `GARMIN_DEVELOPER_KEY` in PowerShell. Never publish your key.

Run `00_Check_Environment.cmd`, then `01_Run_Simulator.cmd`. The scripts discover the current Garmin SDK automatically. For explicit paths, use `tools/Build.ps1 -KeyPath ... -SdkPath ... -Run`.

## Choose a language and preview

The CN package starts in Chinese and the EN package starts in English. Both contain both languages. Open `设置助手.html` for offline sample previews, fields, fonts, colors and backgrounds. Export `config.json`, replace the file in the project root, then rebuild. The control labels are bilingual. Stored device properties can override compiled defaults.

In the simulator choose **Simulation → Trigger App Settings**. On the watch open the watchface's customization menu. Use UP/DOWN to select, START to enter/save and BACK to cancel/return. Choose **Time and appearance → Language** to change language.

## Positions

| Position | Location or purpose |
| --- | --- |
| A0 | Top strip |
| A1 | Upper left icon |
| A2 | Upper center text |
| A3 | Upper right icon |
| A4 | Paired values to the right of the date |
| B0 | Date |
| B1 | Main clock |
| B2 | Seconds |
| B3 | Weekday |
| C0 | Sloping progress bars |
| C1 | Lower left ring and value |
| C2 / C4 | First metric row, left / right |
| C3 / C5 | Second metric row, left / right |
| C6 | Bottom strip |

A0/A2/B0/A4/C6 use a dedicated 16px UI font. C1 digit ink height is 22px. Clock and data digit families are separately selectable; the data choice controls C0, C1 and the four lower slots. Each lower slot offers 28 visible metrics. Long values can be shortened or truncated to preserve boundaries. The root `手表端设置.html` provides the interactive field diagram with bilingual option names.

## Build and install

1. Run `02_Build_For_Watch.cmd` and check the success output.
2. Connect the watch by USB and open its Garmin storage.
3. Copy `bin/Aurora6X.prg` to `GARMIN/APPS`.
4. Safely eject and disconnect.
5. Select Aurora 6X Studio in the watchface menu. Firmware wording can differ.
6. Customize fields and press START to save each choice.

For updates, replace the same PRG filename. Keep `GARMIN/APPS/SETTINGS` and `DATA` intact.

## Troubleshooting

A missing key must be resolved with a real key file, not a folder. Install missing device packages in SDK Manager. A `--` value indicates unavailable or expired data; check sensors and phone synchronization. If settings do not change, verify the project folder and edit stored settings on the watch. Report memory errors with the complete stack, firmware/API version, theme and selected typefaces. See [validation](Validation.en.md) and [data notes](Data.en.md).
