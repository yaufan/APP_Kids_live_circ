/// What the game is made of (docs/design.md): the ages, the scenes (six rooms
/// and five places outside), the weather, the week, the buddies, the clock's
/// pictures, the things to do each day, the chores and the things that just
/// happen. Nothing here changes while playing; game.dart keeps what does.
library;

/// The child's age (parent mode). 小小 does one thing at a time with the way
/// lit up; 大 reads the clock and gets an extra step in each game.
enum Level {
  small('小小', '2～3 歲'),
  big('大', '4～5 歲');

  const Level(this.zh, this.ages);

  final String zh;
  final String ages;
}

/// A scene: a room of the house or a place outside. One fills the screen.
enum Scene {
  living('客廳', 'living room', home: true),
  bedroom('房間', 'bedroom', home: true),
  bathroom('廁所', 'bathroom', home: true),
  kitchen('廚房', 'kitchen', home: true),
  entrance('門口', 'front door', home: true),
  balcony('陽台', 'balcony', home: true),
  street('小街', 'street'),
  park('公園', 'park'),
  school('幼兒園', 'kindergarten'),
  market('超市', 'supermarket'),
  clinic('診所', 'clinic');

  const Scene(this.zh, this.en, {this.home = false});

  final String zh;
  final String en;

  /// A room of the house (the bottom strip shows these).
  final bool home;

  static final rooms = [for (final s in values) if (s.home) s];
  static final places = [for (final s in values) if (!s.home && s != street) s];
}

/// What the sky is like today (the window and the clothes to pick).
enum Weather {
  sun('晴天', 'sunny'),
  rain('下雨', 'rainy'),
  cold('冷天', 'cold'),
  hot('熱天', 'hot'),
  storm('颱風天', 'typhoon');

  const Weather(this.zh, this.en);

  final String zh;
  final String en;

  /// Weather to go out in (a typhoon day stays home).
  bool get goesOut => this != storm;
}

/// The days of the week (Monday is 1, as in DateTime).
abstract final class Week {
  static const zh = ['', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'];
  static const short = ['', '一', '二', '三', '四', '五', '六', '日'];

  static bool weekend(int day) => day >= 6;

  static int next(int day) => day == 7 ? 1 : day + 1;
}

/// The little friend who follows the child's character.
enum Buddy {
  dog('小狗', 'puppy'),
  cat('小貓', 'kitten'),
  rabbit('小兔', 'bunny'),
  duck('小鴨', 'duckling');

  const Buddy(this.zh, this.en);

  final String zh;
  final String en;

  /// Its call (assets/sounds/`buddy_<kind>`.wav).
  String get sound => 'buddy_$name';
}

/// How the child's paper puppet looks (docs/art.md avatar/).
class Avatar {
  const Avatar({this.hair = 1, this.skin = 1, this.shirt = 1});

  static const hairs = 4, skins = 4, shirts = 6;

  final int hair;
  final int skin;
  final int shirt;

  Avatar copyWith({int? hair, int? skin, int? shirt}) => Avatar(hair: hair ?? this.hair, skin: skin ?? this.skin, shirt: shirt ?? this.shirt);

  Map<String, dynamic> toJson() => {'hair': hair, 'skin': skin, 'shirt': shirt};

  factory Avatar.fromJson(Map<String, dynamic>? j) {
    int pick(String k, int max) {
      final v = j?[k];
      return v is int && v >= 1 && v <= max ? v : 1;
    }

    return Avatar(hair: pick('hair', hairs), skin: pick('skin', skins), shirt: pick('shirt', shirts));
  }

  @override
  bool operator ==(Object other) => other is Avatar && other.hair == hair && other.skin == skin && other.shirt == shirt;

  @override
  int get hashCode => Object.hash(hair, skin, shirt);
}

/// The faces (docs/art.md `face_<mood>.svg`).
enum Mood { normal, happy, sleepy, squirm, sad, sick, mouth }

/// The pictures around the clock (assets/art/clock/`t_<icon>.svg`). A task
/// shows as one of these; tasks in a row with the same picture share it.
enum ClockIcon {
  wake('起床'),
  teeth('刷牙'),
  dress('穿衣服'),
  meal('吃飯'),
  school('上學'),
  wash('洗手'),
  play('出去玩'),
  chore('做家事'),
  bath('洗澡'),
  sleep('睡覺'),
  market('買菜'),
  cook('煮飯'),
  nap('午睡');

  const ClockIcon(this.zh);

  final String zh;
}

/// The eight chores; one a day, in turn (docs/design.md 「幫忙做家事」).
enum Chore {
  toys('收玩具', 'tidy the toys', Scene.living, 'toybox'),
  table('擺碗筷', 'set the table', Scene.kitchen, 'table'),
  wipe('擦桌子', 'wipe the table', Scene.kitchen, 'table'),
  laundry('收衣服', 'bring in the laundry', Scene.balcony, 'rack'),
  water('澆花', 'water the plants', Scene.balcony, 'plants'),
  feed('餵小夥伴', 'feed your buddy', Scene.balcony, 'bowl'),
  trash('倒垃圾', 'take out the trash', Scene.balcony, 'bins'),
  sweep('掃地', 'sweep the floor', Scene.living, 'rug');

  const Chore(this.zh, this.en, this.scene, this.target);

  final String zh;
  final String en;
  final Scene scene;

  /// The thing in the scene to tap to start.
  final String target;
}

/// The things to do in a day. [scene] is where, [target] the thing there to
/// tap, [icon] the clock's picture, [free] whether the free version has it.
enum Task {
  wake('起床', 'wake up', Scene.bedroom, 'bed', ClockIcon.wake, free: true),
  teeth('刷牙洗臉', 'brush teeth', Scene.bathroom, 'sink', ClockIcon.teeth, free: true),
  dress('換衣服', 'get dressed', Scene.bedroom, 'wardrobe', ClockIcon.dress),
  breakfast('吃早餐', 'eat breakfast', Scene.kitchen, 'table', ClockIcon.meal, free: true),
  schoolGo('準備上學', 'get ready for school', Scene.entrance, 'bag', ClockIcon.school),
  school('在幼兒園', 'at kindergarten', Scene.school, 'cubby', ClockIcon.school),
  home('回家洗手吃點心', 'home: wash hands, snack', Scene.kitchen, 'sink', ClockIcon.wash),
  park('去公園玩', 'play at the park', Scene.park, 'slide', ClockIcon.play),
  tidy('收玩具', 'tidy up', Scene.living, 'toybox', ClockIcon.chore),
  chore('幫忙做家事', 'help with a chore', Scene.living, 'toybox', ClockIcon.chore),
  dinner('吃晚餐', 'eat dinner', Scene.kitchen, 'table', ClockIcon.meal, free: true),
  bath('洗澡', 'take a bath', Scene.bathroom, 'bathtub', ClockIcon.bath),
  teethNight('刷牙上廁所', 'brush teeth, potty', Scene.bathroom, 'sink', ClockIcon.teeth, free: true),
  sleep('聽故事睡覺', 'story and sleep', Scene.bedroom, 'bed', ClockIcon.sleep, free: true),
  // Weekend only.
  market('去超市買菜', 'shop at the supermarket', Scene.market, 'shelf', ClockIcon.market),
  cook('一起煮飯吃午餐', 'cook lunch together', Scene.kitchen, 'stove', ClockIcon.cook),
  nap('睡午覺', 'nap', Scene.bedroom, 'bed', ClockIcon.nap);

  const Task(this.zh, this.en, this.scene, this.target, this.icon, {this.free = false});

  final String zh;
  final String en;
  final Scene scene;
  final String target;
  final ClockIcon icon;
  final bool free;

  /// The sticker for it (assets/art/rewards/`sticker_<name>.svg`).
  String get sticker => 'sticker_$name';

  /// A weekday, in order (docs/design.md 「平日的一天」).
  static const weekday = [wake, teeth, dress, breakfast, schoolGo, school, home, park, tidy, chore, dinner, bath, teethNight, sleep];

  /// A weekend day (「週末的一天」).
  static const weekend = [wake, teeth, dress, breakfast, market, cook, nap, park, bath, teethNight, sleep];

  /// The ones a parent can turn off (the first and last stay).
  static const optional = [dress, schoolGo, school, home, park, tidy, chore, bath, market, cook, nap];
}

/// Something that just happens, 2～4 times a day (docs/design.md 「偶爾會發生的事」).
/// [scene] is where to go to deal with it (null: right here), [sign] the
/// little picture over the character's head, [mood] the face.
enum Happening {
  pee('想尿尿', 'needs the potty', Scene.bathroom, 'toilet', 'drop', Mood.squirm),
  hungry('肚子餓了', 'is hungry', Scene.kitchen, 'fridge', 'tummy', Mood.sad),
  sleepy('想睡覺', 'is sleepy', Scene.bedroom, 'bed', 'yawn', Mood.sleepy),
  thirsty('口渴了', 'is thirsty', null, null, 'cup_water', Mood.normal),
  sweaty('流汗了', 'is sweaty', null, null, 'sweat', Mood.normal),
  cold('覺得冷', 'is cold', Scene.bedroom, 'wardrobe', 'shiver', Mood.sad),
  sneeze('打噴嚏流鼻水', 'has a runny nose', Scene.clinic, 'doctor', 'tissue', Mood.sick),
  fall('跌倒擦傷', 'fell and scraped a knee', Scene.bathroom, 'sink', 'bandage', Mood.sad),
  mosquito('被蚊子咬', 'a mosquito bite', Scene.bedroom, 'bed', 'mosquito', Mood.sad),
  doorbell('門鈴響了', 'the doorbell', Scene.entrance, 'door', 'doorbell', Mood.normal),
  phone('電話響了', 'the phone', Scene.living, 'phone', 'phone_ring', Mood.normal),
  blackout('停電了', 'a blackout', Scene.living, 'shelf', 'flashlight', Mood.sad),
  garbage('垃圾車來了', 'the garbage truck', Scene.balcony, 'bins', 'garbage_truck', Mood.happy),
  buddyHungry('小夥伴餓了', 'buddy is hungry', Scene.balcony, 'bowl', 'tummy', Mood.normal),
  plant('盆栽枯了', 'the plant wilted', Scene.balcony, 'plants', 'watering_can', Mood.normal),
  rainLaundry('下雨了，收衣服！', 'rain: the laundry!', Scene.balcony, 'rack', 'w_rain', Mood.normal),
  thunder('打雷了', 'thunder', null, null, 'w_storm', Mood.sad),
  earthquake('地震！', 'earthquake!', null, null, 'table_hide', Mood.sad),
  share('小夥伴想玩同一個玩具', 'buddy wants the same toy', Scene.living, 'toybox', 'toy_car', Mood.sad),
  angry('拼圖拼不好，好生氣', 'the puzzle will not fit', Scene.living, 'rug', 'breath_1', Mood.sad),
  spill('牛奶打翻了', 'spilled the milk', Scene.kitchen, 'table', 'food_milk', Mood.sad),
  classmate('同學哭了', 'a classmate is crying', Scene.school, 'classmate_1', 'tissue', Mood.sad);

  const Happening(this.zh, this.en, this.scene, this.target, this.sign, this.mood);

  final String zh;
  final String en;
  final Scene? scene;
  final String? target;
  final String sign;
  final Mood mood;

  /// The ones that can come up while at home (not at school).
  static const atHome = [pee, hungry, sleepy, thirsty, sweaty, cold, sneeze, fall, mosquito, doorbell, phone, blackout, garbage, buddyHungry, plant, rainLaundry, thunder, earthquake, share, angry, spill];
}

/// The safety reminders that come up (docs/design.md 「安全小常識」).
abstract final class Safety {
  static const hotPot = '熱的鍋子不能碰喔！';
  static const socket = '插座不能戳喔！';
  static const holdHands = '過馬路要牽手！';
  static const seatbelt = '坐車要繫安全帶！';
  static const quake = '地震躲桌下，保護頭！';
  static const strangeFood = '不認識的東西不能吃喔！';
  static const thunder = '打雷不怕，我們在家裡很安全。';
}
