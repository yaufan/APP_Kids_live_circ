# 小小生活家

給 2～5 歲小朋友的生活習慣遊戲：幫自己取名字、選一個小角色和一隻小夥伴，一起過一天。看時鐘知道現在該做什麼，走到對的房間，用小遊戲完成刷牙、吃飯、上廁所、睡午覺、上學、幫忙家事；角色偶爾會想尿尿、肚子餓，要注意到牠的需要。目的是把真實生活的作息變熟悉、變好玩，而不是在螢幕上玩很久。

- 設計：[docs/design.md](docs/design.md)，草圖在 `docs/mockups/`，圖和程式的約定在 [docs/art.md](docs/art.md)。
- 和「[畫畫小鎮](https://github.com/yaufan/APP_Kids_Paint)」「[字母寵物](https://github.com/yaufan/APP_Kids_Paint_for_learning_writing)」「[動物小餐廳](https://github.com/yaufan/APP_Kids_Cook)」「[小卡認天下](https://github.com/yaufan/APP_Kids_Card_Game)」「[想一想樂園](https://github.com/yaufan/APP_Kids_Brainstorming)」「[眼尖尖大挑戰](https://github.com/yaufan/APP_Kids_FalseCharge)」「[迷宮小冒險](https://github.com/yaufan/APP_Kids_maze)」是兄弟 APP：同一個作者、同一套技術、不同畫風。
- 不連網、不定位、沒有廣告、沒有帳號；名字只存在手機裡。

## 下載（Android）
- 最新版：[Releases](https://github.com/yaufan/APP_Kids_live_circ/releases/latest)，一般手機下載 `little-life-版本-arm64.apk`。
- 用手機掃描 [docs/download-qr.png](docs/download-qr.png)。

## 目前進度
- 0.1.0（測試版）：取名選角色、六個房間一次一個、小街和四個外面的地方、會轉的時鐘、平日和週末的一天、約 25 個小遊戲、8 種家事、22 種偶爾發生的事、天氣和星期、點東西念名字、貼紙表和房間裝飾、身高尺、休息時間、家長模式、音樂和音效、APP 圖示。立體書風。版本紀錄在 [CHANGELOG.md](CHANGELOG.md)。

## 程式和素材在哪裡
- `app/`：Flutter 程式。`lib/core/` 是內容（`content.dart`）、一天的計畫和時鐘（`day.dart`）、小遊戲的步驟（`steps.dart`）、偶爾發生的事（`events.dart`）、存檔的東西（`game.dart`）、場景的排版（`scenes.dart`）、聲音、語音；`lib/features/` 是取名選角色（`setup/`）、房間和時鐘（`room/`）、小遊戲（`play/`）、貼紙表、睡覺、休息、家長模式。
- `app/assets/scenes/<場景>.json`：每個場景的東西和位置，圖和程式共用。
- `design/art/`：用 Python 畫的圖（立體書風）。`kit.py` 是畫法，`scene.py` 把一個場景畫成 SVG 和 JSON，`room_<房間>.py`、`place_<地方>.py` 是十一個場景，`avatar.py`、`buddy.py`、`clock.py`、`props_*.py`、`rewards.py`、`icon.py`；`python3 build.py all` 全部重畫，`fluttercheck` 用真的 flutter_svg 比對。
- `design/sounds/make_sounds.py`：合成全部的音樂和聲音。
- 測試：在 `app/` 裡 `flutter test`；完整流程 `flutter test test/flow_test.dart`，截圖在 `app/build/screenshots/`。

## 授權
- 非商業使用授權：自己、家人使用，或學校、非營利團體的教學，都可以免費使用、修改、分享，要註明出處。
- 商業用途（販賣、收費、廣告、上架）要先取得作者書面同意。也不可以拿來訓練 AI。
- 細節見 [LICENSE](LICENSE)；別人做的部分（字型）見 [NOTICE.md](NOTICE.md)。
