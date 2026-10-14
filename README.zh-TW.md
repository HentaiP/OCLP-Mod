# OCLP-Mod — Intel Tahoe fork

以 OCLP-Mod 的 GitHub fork 為定位，整合官方 Tahoe 開發基底與受限的 Intel 無線支援。
這是獨立分支，不代表 Dortania、laobamac 或 KGP 的官方發行或背書。

This product includes software developed by Dortania and OpenCore Legacy Patcher contributors.
This product includes software developed by Dortania and OCLP contributors.

此项目基于 laobamac/OCLP-Mod (https://github.com/laobamac/OCLP-Mod) 构建，
受 OCLP-Mod 私人开源协议约束。未经王孝慈书面授权不得用于商业衍生品。

## 差異與現況

- 保留官方 Tahoe 圖形、USB、無線 patch 字典與安全檢查，使用 PatcherSupportPkg 2.0.3。
- Intel PCI 白名單 87 項；不是每張卡都已做實機驗收，BE200 不包含。
- Tahoe 建置主機選 KGP AirportItlwm-Tahoe 正式 1.0.0；較舊主機選 Ventura 2.3.0。
- IntelBluetoothFirmware／IntelBTPatcher 固定 2.5.0，BlueToolFixup 基準 2.7.2。
- payload 雜湊與版本檢查維持 fail-closed，不略過安全 preflight 或未知 plugin 拒絕。
- 保留最後重新 ad-hoc 簽章與 compiled CLI 產出的 EFI 在程式結束後仍留存的修正。

已有原生 x86_64 App／Pkg 編譯、AX210 真實偵測、完整 CLI EFI 生成、13/13 回歸測試紀錄。
維護者另外回報私有建置已測試可用；詳細範圍見 [VALIDATION.md](VALIDATION.md)。
既有 App 為 ad-hoc，Pkg 未簽章，沒有 Apple 公證；它們未包含在這個原始碼公開包。
也不宣稱所有硬體、舊 macOS、Apple Silicon、AirDrop 或睡醒都已驗收。

## 使用與發佈

先閱讀 [建置說明](BUILDING.md)、[Intel profile](INTEL_TAHOE.md) 與 [授權／來源](THIRD_PARTY_NOTICES.md)。
本包只有原始碼與固定 manifest；Intel 新增二進位 payload 須另行取得並通過匯入工具的雜湊檢查。
現有 Intel Bluetooth 2.5.0 二進位的精確源碼版本尚未核實，不在公開包內散布。
不能把主機 OS 判斷當成外接目標機的 OS；新產生的 EFI 也不會自動合併既有 picker／多系統設定。

OCLP-Mod 上游已於 2026 年 6 月宣告封存。本分支保留其公開歷史與所有來源授權；
不保留其整套中文介面或 SimpleHacAPI 服務，也不將衍生部分重新宣稱為不受限制的 BSD／MIT。
按原授權的 GitHub fork 例外準備；獨立軟體包或商業散布是不同的授權範圍。
