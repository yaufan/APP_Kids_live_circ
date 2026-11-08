import '../core/content.dart';

/// Everything the app says, in Traditional Chinese (Taiwan).
abstract final class Strings {
  static const appName = '小小生活家';

  // Setup.
  static const setupTitle = '你好！你叫什麼名字？';
  static const nameHint = '請爸爸媽媽幫忙打名字（不打也可以）';
  static const pickLook = '選一個自己的樣子';
  static const hair = '頭髮';
  static const skin = '膚色';
  static const shirt = '衣服';
  static const pickBuddy = '選一隻小夥伴';
  static const start = '開始過一天！';
  static String welcome(String name, Buddy b) => '$name，你好！我是${b.zh}，我們一起過一天吧！';

  // The room.
  static String nowDo(String name, Task t) => '$name，該${t.zh}囉！';
  static String goTo(Scene s) => '去${s.zh}！';
  static String here(Task t) => '點一下${_target(t)}，開始${t.zh}。';
  static String _target(Task t) => switch (t) {
        Task.wake || Task.sleep || Task.nap => '床',
        Task.teeth || Task.teethNight => '洗手台',
        Task.dress => '衣櫃',
        Task.breakfast || Task.dinner => '餐桌',
        Task.schoolGo => '書包',
        Task.school => '格子',
        Task.home => '水槽',
        Task.park => '溜滑梯',
        Task.tidy || Task.chore => '發亮的東西',
        Task.bath => '浴缸',
        Task.market => '架子',
        Task.cook => '爐子',
      };
  static String happening(String name, Happening h) => switch (h) {
        Happening.pee => '$name想尿尿了！快去廁所。',
        Happening.hungry => '$name肚子咕嚕咕嚕叫，去廚房找點心。',
        Happening.sleepy => '$name打哈欠了，去房間休息一下。',
        Happening.thirsty => '$name口渴了，喝水吧。',
        Happening.sweaty => '$name流汗了，擦擦汗、喝水。',
        Happening.cold => '$name覺得冷，去房間穿外套。',
        Happening.sneeze => '哈啾！$name感冒了，擦鼻涕、去診所。',
        Happening.fall => '哎呀，$name跌倒了，去廁所洗乾淨。',
        Happening.mosquito => '被蚊子咬了，癢癢的，去房間擦藥。',
        Happening.doorbell => '叮咚！門鈴響了，去門口看看。',
        Happening.phone => '鈴鈴鈴！電話響了，去客廳接。',
        Happening.blackout => '停電了！去客廳找手電筒。',
        Happening.garbage => '垃圾車的音樂來了！去陽台倒垃圾。',
        Happening.buddyHungry => '小夥伴餓了，去陽台餵牠。',
        Happening.plant => '盆栽垂下來了，去陽台澆水。',
        Happening.rainLaundry => '下雨了！去陽台收衣服。',
        Happening.thunder => '轟隆隆，打雷了。不怕不怕。',
        Happening.earthquake => '地震！躲到桌子下面！',
        Happening.share => '小夥伴也想玩那個玩具，去客廳看看。',
        Happening.angry => '拼圖拼不好，$name好生氣。去客廳深呼吸。',
        Happening.spill => '牛奶打翻了，去廚房擦一擦。',
        Happening.classmate => '同學哭了，去看看。',
      };
  static const eventDone = '好棒，注意到了！';
  static String taskDone(Task t) => '${t.zh}完成，得到一張貼紙！';
  static const allDone = '今天的事都做完了！小夥伴送你一樣裝飾！';
  static const goodNight = '晚安，整個家都睡了。';
  static const newDay = '新的一天！';
  static const stickers = '貼紙表';
  static const parent = '家長';
  static const clockOpen = '時鐘：現在該做什麼？';
  static String clockSay(Task t) => '現在是${t.icon.zh}的時間。';
  static String dayLine(int weekday, Weather w) => '${Week.zh[weekday]}，${w.zh}。';
  static String weekendNote(int weekday) => Week.weekend(weekday) ? '今天不用上學！' : '明天要上學。';
  static const outside = '出門';
  static const back = '回去';
  static const toStreet = '回小街';
  static const home = '回家';
  static const storm = '颱風天，今天在家玩。';
  static const stairsUp = '上樓';
  static const stairsDown = '下樓';
  static const left = '往左';
  static const right = '往右';

  // Playing.
  static const next = '下一步';
  static const again = '再一次';
  static const done = '好棒！';
  static const praise = ['好棒！', '做得真好！', '你好厲害！', '太棒了！', '就是這樣！'];
  static const bounce = '不是這裡喔，再試試。';
  static const holdOn = '按著不要放…';
  static const letGo = '可以放開了！';
  static const stop = '先不做了';

  // Sticker chart.
  static String stickerTitle(String name) => '$name的貼紙表';
  static String todayCount(int done, int all) => '今天 $done／$all';
  static String totalCount(int n) => '一共 $n 張貼紙';
  static String decoLine(int n) => n == 0 ? '一天全部做完，家裡就多一樣裝飾。' : '家裡有 $n 樣裝飾了！';
  static String heightLine(int n) => n == 0 ? '集滿一週，長高一格！' : '長高了 $n 格！';

  // Night.
  static const nightTitle = '今天辛苦了';
  static const nightTap = '點一下，到明天早上';

  // Resting.
  static const restTitle = '該休息了';
  static const restLine = '小角色睡著了。\n換你去做了！\n去刷牙、喝水、看看遠方吧。';

  // Parent gate (as in the sibling apps).
  static const callParent = '請爸爸媽媽來幫忙喔！';
  static const parentGateTitle = '家長確認';
  static String gateQuestion(String a, String b) => '$a 加 $b 等於多少？';
  static const gateRules = '答錯三次要等一分鐘。';
  static const wrongAnswer = '不對喔，換一題。';
  static String gateWait(int s) => '請等 $s 秒再試';
  static const backspace = '刪掉';
  static const cancel = '取消';

  // Parent mode.
  static const parentTitle = '家長模式';
  static const child = '小朋友';
  static const changeName = '名字';
  static const changeLook = '重新選角色';
  static const age = '年齡（難度）';
  static String levelLine(Level l) => '${l.zh}（${l.ages}）';
  static const ageNote = '小小：一次一件事，該去的房間會發亮、角色自己走過去。大：自己看時鐘找房間，小遊戲多一步（扣釦子、擺碗筷、分四種回收）。';
  static const playTime = '每次可以玩多久';
  static String minutes(int m) => '$m 分鐘';
  static const playTimeNote = '時間到了角色也睡覺、整個家變暗，APP 會說「換你去做了！」。要家長解開，或等一個小時，才能再玩。';
  static const playOn = '讓小朋友再玩一次（重新計時）';
  static const resting = '現在是休息時間。';
  static const routines = '一天要做哪些事';
  static const routinesNote = '沒有上幼兒園就把上學關掉；起床、刷牙、吃飯、睡覺一定有。';
  static const sound = '聲音';
  static const music = '背景音樂';
  static const effects = '音效';
  static const voice = '念出要做什麼和東西的名字';
  static const english = '說完國語，再說一次英文（toothbrush）';
  static const progress = '最近幾天';
  static const progressNone = '還沒過完一天。';
  static String progressLine(int weekday, int done, int all) => '${Week.zh[weekday]}：做完 $done／$all';
  static String skippedMost(Task t, int n) => '最常跳過：${t.zh}（$n 次）';
  static const together = '生活中一起做';
  static const tips = [
    '把家裡的作息貼在牆上，用圖畫，讓小朋友自己看「接下來做什麼」。',
    '刷牙時一起唱一首歌，唱完剛好刷完。',
    '吃飯前讓小朋友擺碗筷：「我們有幾個人？」',
    '出門前一起看窗外：「今天要穿什麼？」',
    '注意到小朋友夾腿、揉眼睛時，說出來：「你是不是想尿尿？」',
  ];
  static const fullVersion = '完整版';
  static const fullNote = '免費版有起床、刷牙、吃飯、睡覺；完整版有全部的事、外面的地方和裝飾。（測試版先全部打開。）';
  static const fullSwitch = '打開完整版（測試用）';
  static const about = '關於';
  static const privacy = '不連網、不定位、沒有廣告、沒有帳號；名字和紀錄只存在這支手機裡，不會傳給任何人。';
  static String version(String v) => '版本 $v';
}
