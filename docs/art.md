# 圖的約定：圖和程式共用

畫風只有一種：**立體書風**（紙片一層一層立起來，有紙的厚度和影子；柔和的粉紅、薄荷、奶油黃；Q 版大頭紙偶；家具有小臉）。圖由 `design/art/` 的 Python 程式畫成 SVG。每個房間、每個外面的地方是一個「場景」：一張背景加上一個一個分開的東西，位置寫在 `app/assets/scenes/<場景>.json`，程式照它擺、照它判斷點到什麼。

## 檔案在哪裡（`app/assets/art/`）
### 角色（`avatar/`）：拼起來的紙偶，`viewBox="0 0 200 260"`，腳底在下緣
- 身體：`body_<pose>_<shirt>.svg`，pose：`stand`、`sit`、`lie`（躺著，睡覺用，viewBox 一樣，畫成橫的也可以，程式會知道）；shirt：`1`～`6`（紅、黃、綠、藍、紫、粉）。
- 頭：`head_<skin>.svg`，skin：`1`～`4`（由淺到深），含耳朵和脖子，沒有五官。
- 臉：`face_<mood>.svg`：`normal`、`happy`、`sleepy`（閉眼）、`squirm`（想尿尿，皺眉咬唇）、`sad`、`sick`（紅鼻子）、`mouth`（張大嘴巴，刷牙和看喉嚨用，牙齒要畫清楚）。
- 頭髮：`hair_<n>.svg`，`1`～`4`（短髮、妹妹頭、馬尾、捲髮），顏色固定深棕。
- 程式把 body、head、face、hair 疊在一起；三個 pose 的頭都在同一個位置（lie 除外，lie 的頭在左邊）。`avatar/layout.json` 寫每個 pose 頭的中心和大小。
### 小夥伴（`buddy/`）：`<kind>_<pose>.svg`，`viewBox="0 0 160 160"`
kind：`dog`、`cat`、`rabbit`、`duck`；pose：`stand`、`sleep`、`happy`（跳起來）、`eat`。
### 時鐘（`clock/`）
- `face.svg`（木紋底的鐘面，有小臉）300×300，`hand.svg` 60×300（指針，從中心往上）。
- 十三個時段圖案，各 100×100，有小臉：`t_wake`（太陽）、`t_teeth`（牙刷）、`t_dress`（上衣）、`t_meal`（碗）、`t_school`（書包）、`t_wash`（洗手的泡泡手）、`t_play`（球）、`t_chore`（掃把）、`t_bath`（浴缸）、`t_sleep`（月亮）、`t_market`（推車）、`t_cook`（鍋子）、`t_nap`（枕頭）。時鐘的圈不是真的時間：一天的事照順序繞一圈，連續同一個圖案的事共用一個位置。
- 天氣：`w_sun`、`w_rain`、`w_cold`（雪花）、`w_hot`（太陽加汗）、`w_storm`（颱風雲）各 100×100。
### 場景（`scenes/<場景>/`）
場景：`living` 客廳、`bedroom` 房間、`bathroom` 廁所、`kitchen` 廚房、`entrance` 門口、`balcony` 陽台、`street` 小街、`park` 公園、`school` 幼兒園、`market` 超市、`clinic` 診所。
- `bg.svg`，`viewBox="0 0 600 800"`：牆、地板、窗外天空（天空留白給程式換顏色的地方用 `#SKY` 當填色，程式會替換成當時的天色），不含可以點的東西。
- 每樣東西一個檔 `<id>.svg`，透明底，viewBox 的寬高比和它的框一樣，剛好畫滿框。有變化的東西用 `<id>_<state>.svg`（例如 `curtain_open`、`curtain_closed`、`lamp_on`、`lamp_off`、`plant_wilt`、`toybox_full`）。
- 裝飾品（貼紙表集滿送的）：`deco_<n>.svg`，每個場景 3 個。
- 每個場景一定要有的東西（程式會找這些 id）：
  - `living`：`sofa`、`toybox`（`""`/`full`）、`phone`、`window`、`stairs`、`lamp`（`on`/`off`）、`rug`、`table`、`shelf`、`plant`（`""`/`wilt`）、`tv`、`picture`。
  - `bedroom`：`bed`、`wardrobe`、`nightlight`（`on`/`off`）、`curtain`（`open`/`closed`，後面是窗，用 `#SKY`）、`book`、`height`（身高尺）、`rug`、`toybox_small`。
  - `bathroom`：`sink`、`mirror`、`toilet`（`closed`/`open`）、`bathtub`、`towel`、`toothbrush_cup`、`window`。
  - `kitchen`：`fridge`、`table`、`sink`、`stove`、`cupboard`、`window`、`chair`。
  - `entrance`：`door`、`shoerack`、`bag`、`umbrella`、`helmet`、`mat`。
  - `balcony`：`plants`（`""`/`wilt`）、`rack`（曬衣架，`""`/`empty`）、`bowl`（小夥伴的碗）、`bins`（垃圾桶和回收桶）、`railing`、`watering_can`。
  - `street`：`home`（自己家的門）、`park`、`school`、`market`、`clinic`（四個地方的門面，有招牌圖案）、`traffic_light`、`bus`。
  - `park`：`slide`、`swing`、`sandbox`、`ball`、`bench`、`tree`、`flower`。
  - `school`：`cubby`（三格、記號是星星／愛心／花）、`teacher`、`classmate_1`、`classmate_2`、`mat`、`blackboard`、`toyshelf`。
  - `market`：`shelf`、`cart`、`cashier`、`fridge`（冷藏櫃）、`sign`、`basket`。
  - `clinic`：`doctor`、`desk`、`bed`、`poster`、`scale`、`plant`。
### 小遊戲的道具（`props/`），各 100×100 除非另外寫
刷牙：`toothbrush`、`toothpaste`、`cup`、`mouth_big`（400×300，張嘴，上下排牙齒分清楚，牙齒上有可以蓋掉的髒點用 `#DIRT` 填色）。
洗手洗澡：`soap`、`tap_on`、`tap_off`、`towel`、`bubble`、`hairdryer`、`bathtub_full`（300×200）。
上廁所：`toilet_open`、`toilet_closed`、`paper`、`flush`。
穿衣服：`cloth_tshirt`、`cloth_jacket`、`cloth_raincoat`、`cloth_shorts`、`cloth_pants`、`cloth_hat`、`cloth_boots`、`cloth_shoes_l`、`cloth_shoes_r`。
吃飯：`plate`（300×300，四格：飯、菜、肉、水果，格子有淡淡的圖案）、`food_rice`、`food_veg`、`food_meat`、`food_fruit`、`food_apple`、`food_banana`、`food_carrot`、`food_milk`、`food_egg`、`food_fish`、`spoon`、`bowl`、`chopsticks`、`cup_water`、`cup_water_full`。
上學：`bag_open`、`item_bottle`、`item_hanky`、`item_book`、`bus`（300×200，娃娃車有臉）、`seatbelt`。
收玩具和家事：`toy_car`、`toy_block`、`toy_doll`、`toy_ball`、`box_car`、`box_block`、`box_doll`（箱子上有圖示）、`rag`、`stain`、`broom`、`dustpan`、`crumbs`、`sock_<n>`（1～4 雙，`sock_<n>_a`、`sock_<n>_b` 一樣的兩隻）、`shirt_hanging`、`peg`、`watering_can`、`trash_bag`、`recycle_paper`、`recycle_bottle`、`recycle_food`、`bin_trash`、`bin_paper`、`bin_bottle`、`bin_food`、`garbage_truck`（300×200，有臉、有音符）。
公園和街：`traffic_light_red`、`traffic_light_green`、`slide`（200×200）、`swing`（200×200）、`sandbox`（200×150）、`ball`、`shell`。
幼兒園：`cubby`（自己的格子，上面有角色的記號）、`teacher`（200×260）、`classmate_<n>`（1～3，200×260）、`mat`（午睡墊）、`snack_plate`。
超市：`cart`（200×200）、`shelf`（300×200）、`cashier`（200×260）、`list`（購物清單，三格）、`bag_shop`。
診所：`thermometer`、`stethoscope`、`syringe`（圓圓的、不可怕）、`medicine`、`doctor`（200×260）、`sticker_brave`。
小遊戲另外會用到：`blanket`、`blanket_folded`、`button`、`umbrella`、`hands_clap`、`footprint`、`shoe_rack`、`table_top`（桌面 300×150）、`buddy_bowl`、`kibble_bag`、`temp_hot`、`temp_warm`、`temp_cold`（三杯水，紅／剛好／藍）、`lotion`、`hands`（一雙手 200×150）、`pot`（鍋子）、`basket`、`shovel`、`dirt`（髒點）、`cubby_1`、`cubby_2`、`cubby_3`（格子，記號星星／愛心／花；取代 `cubby`）、`book_open`。
偶爾的事：`drop`（想尿尿的小水滴）、`tummy`（咕嚕）、`yawn`（哈欠的 Z）、`sweat`、`shiver`、`tissue`、`bandage`、`mosquito`、`flashlight`、`doorbell`、`phone_ring`、`grandma`（200×260）、`mailman`（200×260）、`package`、`table_hide`（桌子底下躲的樣子 300×200）、`breath_1`～`breath_3`（深呼吸的三個泡泡）。
### 獎勵（`rewards/`）
- `sticker_<task>.svg` 每件事一張貼紙，task 是程式的名字：`wake teeth dress breakfast schoolGo school home park tidy chore dinner bath teethNight sleep market cook nap`（圓形 200×200，和時段圖案同一套可愛風）；`chart.svg` 貼紙表的木板底 600×800。
- `house_small.svg` 600×500：整棟房子的小圖（只在貼紙表和睡覺動畫用），房間用 `#ROOM_<id>` 填色，程式變亮變暗。
- `height.svg` 100×600 身高尺。

## 場景 JSON（`app/assets/scenes/<場景>.json`）
```json
{
  "id": "living", "zh": "客廳", "en": "living room",
  "exits": {"left": "kitchen", "right": "entrance", "up": "bedroom"},
  "stand": {"x": 0.42, "y": 0.86, "w": 0.34, "h": 0.5},
  "buddy": {"x": 0.68, "y": 0.86, "w": 0.2, "h": 0.2},
  "things": [
    {"id": "sofa", "zh": "沙發", "en": "sofa", "x": 0.25, "y": 0.72, "w": 0.4, "h": 0.22, "z": 10},
    {"id": "toybox", "zh": "玩具箱", "en": "toy box", "x": 0.82, "y": 0.78, "w": 0.2, "h": 0.16, "z": 20, "states": ["", "full"]},
    {"id": "window", "zh": "窗戶", "en": "window", "x": 0.22, "y": 0.3, "w": 0.3, "h": 0.26, "z": 5}
  ],
  "decos": [{"id": "deco_1", "zh": "牆上的畫", "x": 0.6, "y": 0.28, "w": 0.14, "h": 0.12}]
}
```
- 東西的 `x`、`y` 是框的中心，`w`、`h` 是寬高，都是 0～1，相對於 600×800 的場景。`stand` 是角色站的地方、`buddy` 是小夥伴站的地方：這兩個的 `y` 是框的**下緣**（腳底），不是中心。角色和小夥伴畫在 z=50，東西的 z 都小於 50。
- `exits` 的鍵：`left`、`right`、`up`（樓梯）、`down`、`out`（出門到小街）、`back`（從外面回小街）；值是場景 id。小街的 `things` 就是通往各地方的入口（id 和場景 id 一樣：`home`、`park`、`school`、`market`、`clinic`）。
- 每樣東西點一下會念 `zh`（家長開了英文就再念 `en`）。
- `states`：有變化的東西，程式換檔名後綴。
- `exits`：左右箭頭和樓梯通到哪裡。

## flutter_svg 的限制
不能用 `<filter>`、`<mask>`、`<style>`／`style=`、CSS、`<text>`、`<image>`、`<pattern>`、混色模式。紙的厚度和影子要用多畫一層偏移的深色形狀來做。每個元素都要寫 `fill`／`stroke`。每個檔案小於約 70 KB。用真的 flutter_svg 和 Chromium 比對過（`design/art/build.py fluttercheck`）。
