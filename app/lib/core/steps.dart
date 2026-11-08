import 'dart:math' as math;

import 'content.dart';

/// The little games (docs/design.md 「小遊戲」): each thing to do is a short
/// list of steps, and every step is one of five kinds a single screen knows
/// how to show. Nothing can be failed: a wrong drop bounces back, a wrong
/// choice gets a gentle word and another go.
///
/// Pictures are named as in docs/art.md: a plain name is a prop
/// (`assets/art/props/<name>.svg`), `scene/thing` is a thing in a scene, and
/// `@avatar`, `@head`, `@body`, `@buddy` are the puppets the program draws.
sealed class Step {
  const Step({required this.say, this.en, this.sfx = 'yay', this.mood = Mood.normal, this.safety});

  /// What the buddy says (spoken, and shown for the grown-up).
  final String say;
  final String? en;

  /// Played when the step is done.
  final String sfx;

  /// The character's face during the step.
  final Mood mood;

  /// A safety reminder said with the step (docs/design.md 「安全小常識」).
  final String? safety;
}

/// Tap each picture once (the same name twice means two taps). [result]
/// replaces the picture once it is tapped (curtain_closed → curtain_open).
class TapStep extends Step {
  const TapStep(this.props, {required super.say, super.en, this.result, this.tapSfx = 'tap', super.sfx, super.mood, super.safety});

  final List<String> props;
  final String? result;

  /// Played at each tap.
  final String tapSfx;
}

/// Rub a finger over [base] until the dirt is gone (brushing, washing,
/// wiping, sweeping, digging). [dirt] is scattered over it by the program
/// and wiped away where [tool] passes; [strokes] is how much rubbing.
class ScrubStep extends Step {
  const ScrubStep({required this.base, required this.tool, required super.say, super.en, this.dirt, this.strokes = 8, this.loopSfx, this.reveal, super.sfx, super.mood, super.safety});

  final String? base;
  final String tool;
  final String? dirt;
  final int strokes;

  /// Played while rubbing.
  final String? loopSfx;

  /// Shows up when the rubbing is done (the shell in the sand).
  final String? reveal;
}

/// Drag each item to a slot. An item with a [DragItem.slot] goes only there;
/// without one, anywhere free. Wrong slot: it bounces back with a gentle
/// word. Items that belong nowhere (a toy in the school bag) are left over
/// and the step is done without them.
class DragStep extends Step {
  const DragStep({required this.items, required this.slots, required super.say, super.en, this.board, this.dropSfx = 'pop', this.wrong, super.sfx, super.mood, super.safety});

  final List<DragItem> items;
  final List<DragSlot> slots;

  /// A big picture behind the slots (the plate, the body).
  final String? board;
  final String dropSfx;

  /// Said when an item is dropped in the wrong place.
  final String? wrong;

  /// The items that have a home.
  List<DragItem> get needed => [for (final i in items) if (i.slot != null || slots.any((s) => s.takes(i))) i];
}

class DragItem {
  const DragItem(this.prop, {this.slot, this.zh});

  final String prop;

  /// The slot it belongs in (null: any that takes it).
  final String? slot;

  /// Its name, said when it is picked up.
  final String? zh;
}

class DragSlot {
  const DragSlot(this.id, {this.prop, this.zh, this.capacity = 1, this.accepts, this.x, this.y});

  final String id;

  /// Its picture (null: drawn as a soft outline by the program).
  final String? prop;
  final String? zh;
  final int capacity;

  /// Which props it takes when an item has no slot of its own (null: any).
  final Set<String>? accepts;

  /// Where on the board it sits (0～1; null: laid out in a row).
  final double? x, y;

  bool takes(DragItem i) => i.slot == id || (i.slot == null && (accepts == null || accepts!.contains(i.prop)));
}

/// Tap the right picture of two or three (the clothes for the weather, the
/// wilted plant, the green light). Wrong: [whyWrong] and another go.
class ChooseStep extends Step {
  const ChooseStep({required this.options, required this.good, required super.say, super.en, this.whyWrong, super.sfx, super.mood, super.safety});

  final List<Choice> options;
  final Set<String> good;
  final String Function(String picked)? whyWrong;
}

class Choice {
  const Choice(this.prop, this.zh, {this.en});

  final String prop;
  final String zh;
  final String? en;
}

/// Press and hold [prop] for [seconds] (sitting on the potty, waiting at
/// the red light, a deep breath, watering). With [tooLong], letting go only
/// after that many seconds is "too much" and it starts over (the plant
/// overflows): learning "just right".
class HoldStep extends Step {
  const HoldStep({required this.prop, required super.say, super.en, this.seconds = 3, this.tooLong, this.loopSfx, this.result, this.tooMuch, super.sfx, super.mood, super.safety});

  final String prop;
  final int seconds;
  final int? tooLong;
  final String? loopSfx;
  final String? result;
  final String? tooMuch;
}

/// One short bedtime story a night (docs/design.md 「睡午覺／睡覺」).
const stories = [
  '小兔子找不到月亮，原來月亮躲在雲後面，跟牠說晚安。',
  '小熊刷完牙，牙齒亮亮的，星星都來看。',
  '小鴨子學游泳，撲通撲通，媽媽在旁邊拍拍手。',
  '小貓咪把玩具收好，玩具們在箱子裡睡著了。',
  '小狗狗幫忙澆花，花開了一朵給牠，牠開心地搖尾巴。',
  '小象洗澡噴水，泡泡飛到天上變成雲。',
  '小鳥排隊回家，一個接一個，誰都沒有擠。',
];

/// The steps for [task] today. [chore] is the chore of the day (for
/// [Task.chore]); [weather] picks the clothes; [rnd] shuffles the shopping.
List<Step> planTask(Task task, {required Level level, required Weather weather, required Chore chore, required math.Random rnd, int family = 3}) {
  final big = level == Level.big;
  return switch (task) {
    Task.wake => [
        const TapStep(['curtain_closed'], result: 'curtain_open', say: '拉開窗簾，太陽進來了！', en: 'Open the curtains!', tapSfx: 'curtain', sfx: 'light_on'),
        const TapStep(['@avatar'], say: '伸個懶腰，嗯～', en: 'Stretch!', tapSfx: 'stretch', mood: Mood.sleepy),
        if (big) const TapStep(['blanket'], result: 'blanket_folded', say: '把被子摺好。', en: 'Fold the blanket.', tapSfx: 'blanket'),
      ],
    Task.teeth => [..._teeth(big), if (big) ..._face()],
    Task.teethNight => [..._teeth(big), ..._toilet(big)],
    Task.dress => _dress(weather, big),
    Task.breakfast => [if (big) _setTable(family), ..._eat(big)],
    Task.dinner => [if (big) _setTable(family), ..._eat(big), const DragStep(items: [DragItem('bowl', slot: 'sink', zh: '碗')], slots: [DragSlot('sink', prop: 'kitchen/sink', zh: '水槽')], say: '吃飽了，碗拿去水槽。', en: 'Take the bowl to the sink.', dropSfx: 'dishes')],
    Task.schoolGo => [
        DragStep(
          items: [const DragItem('item_bottle', zh: '水壺'), const DragItem('item_hanky', zh: '手帕'), const DragItem('item_book', zh: '聯絡簿'), if (big) const DragItem('toy_car', zh: '玩具車')],
          slots: const [DragSlot('bag', prop: 'bag_open', zh: '書包', capacity: 3, accepts: {'item_bottle', 'item_hanky', 'item_book'})],
          say: '書包要裝三樣：水壺、手帕、聯絡簿。',
          en: 'Pack the bottle, hanky and notebook.',
          dropSfx: 'bag_zip',
          wrong: '玩具不用帶去學校喔。',
        ),
        const DragStep(
          board: '@avatar',
          items: [DragItem('cloth_shoes_l', slot: 'foot_l', zh: '左腳的鞋'), DragItem('cloth_shoes_r', slot: 'foot_r', zh: '右腳的鞋')],
          slots: [DragSlot('foot_l', zh: '左腳', x: 0.36, y: 0.93), DragSlot('foot_r', zh: '右腳', x: 0.64, y: 0.93)],
          say: '穿鞋子，左腳、右腳。',
          en: 'Shoes on: left foot, right foot.',
          dropSfx: 'shoes',
          wrong: '這是另一隻腳的鞋喔。',
        ),
        ChooseStep(
          options: const [Choice('cloth_hat', '帽子', en: 'hat'), Choice('umbrella', '雨傘', en: 'umbrella'), Choice('cloth_jacket', '外套', en: 'jacket')],
          good: {
            switch (weather) {
              Weather.rain || Weather.storm => 'umbrella',
              Weather.cold => 'cloth_jacket',
              Weather.sun || Weather.hot => 'cloth_hat',
            }
          },
          say: '今天${weather.zh}，要帶什麼出門？',
          en: 'It is ${weather.en}. What do we take?',
          whyWrong: (p) => switch (weather) {
            Weather.rain || Weather.storm => '下雨要帶雨傘喔。',
            Weather.cold => '冷冷的，要穿外套喔。',
            _ => '太陽大，戴帽子才不會熱。',
          },
          sfx: 'hat',
        ),
        const TapStep(['entrance/door'], say: '跟家裡說再見，掰掰！', en: 'Bye-bye!', tapSfx: 'bye', sfx: 'door', mood: Mood.happy),
        const TapStep(['seatbelt'], say: '坐娃娃車，繫好安全帶！', en: 'On the bus: seatbelt on!', tapSfx: 'seatbelt', sfx: 'bus_ride', safety: Safety.seatbelt),
      ],
    Task.school => [
        const DragStep(
          items: [DragItem('bag_open', slot: 'cubby_1', zh: '書包')],
          slots: [DragSlot('cubby_1', prop: 'cubby_1', zh: '星星的格子'), DragSlot('cubby_2', prop: 'cubby_2', zh: '愛心的格子'), DragSlot('cubby_3', prop: 'cubby_3', zh: '花花的格子')],
          say: '書包放進自己的格子，你的記號是星星！',
          en: 'Put your bag in your cubby: the star.',
          wrong: '這不是你的格子，找找星星。',
        ),
        const TapStep(['teacher', 'classmate_1', 'classmate_2'], say: '老師早安！同學早安！', en: 'Good morning, teacher!', tapSfx: 'bye', sfx: 'clap', mood: Mood.happy),
        const TapStep(['hands_clap', 'hands_clap', 'hands_clap'], say: '一起唱歌拍拍手！', en: 'Sing and clap!', tapSfx: 'clap', sfx: 'sing', mood: Mood.happy),
        const TapStep(['snack_plate', 'snack_plate'], say: '點心時間，慢慢吃。', en: 'Snack time.', tapSfx: 'chew', sfx: 'yum'),
        const HoldStep(prop: 'mat', say: '午睡時間，躺好、閉上眼睛。', en: 'Nap time: lie down, close your eyes.', seconds: 3, loopSfx: 'snore', mood: Mood.sleepy),
        if (big)
          const DragStep(
            items: [DragItem('@avatar', zh: '我'), DragItem('classmate_1', zh: '同學'), DragItem('classmate_2', zh: '同學')],
            slots: [DragSlot('q1', prop: 'footprint', zh: '第一個'), DragSlot('q2', prop: 'footprint', zh: '第二個'), DragSlot('q3', prop: 'footprint', zh: '第三個')],
            say: '放學排隊，一個接一個，不推不擠。',
            en: 'Line up to go home.',
            sfx: 'line_up',
          )
        else
          const TapStep(['footprint'], say: '放學排隊囉！站到腳印上。', en: 'Line up!', tapSfx: 'line_up', sfx: 'bell'),
      ],
    Task.home => [
        const DragStep(
          items: [DragItem('cloth_shoes_l', zh: '鞋子'), DragItem('cloth_shoes_r', zh: '鞋子')],
          slots: [DragSlot('rack', prop: 'shoe_rack', zh: '鞋櫃', capacity: 2)],
          say: '回家了！脫鞋子，放到鞋櫃。',
          en: 'Home! Shoes on the rack.',
          dropSfx: 'shoes',
        ),
        ..._handwash(big),
        const TapStep(['food_apple', 'food_apple'], say: '吃點心，蘋果脆脆的。', en: 'Snack time: an apple.', tapSfx: 'chew', sfx: 'yum'),
        _drink,
      ],
    Task.park => [
        const HoldStep(prop: 'traffic_light_red', say: '紅燈停，等一下。', en: 'Red light: stop and wait.', seconds: 2, loopSfx: 'traffic_wait', result: 'traffic_light_green', sfx: 'traffic_go'),
        const TapStep(['traffic_light_green'], say: '綠燈了！左看、右看，牽好手再走。', en: 'Green! Look left, look right, hold hands.', tapSfx: 'walk', sfx: 'walk', safety: Safety.holdHands),
        if (big) const TapStep(['classmate_1'], say: '先輪到別的小朋友，我們排隊等一下。', en: 'Wait your turn.', tapSfx: 'tap', sfx: 'pop'),
        const TapStep(['slide'], say: '輪到你了！溜滑梯，咻～', en: 'Your turn! Whee!', tapSfx: 'slide', sfx: 'yay', mood: Mood.happy),
        const TapStep(['swing', 'swing', 'swing'], say: '推推鞦韆，盪高高！', en: 'Push the swing!', tapSfx: 'swing', sfx: 'yay', mood: Mood.happy),
        const ScrubStep(base: 'sandbox', tool: 'shovel', say: '挖挖沙，裡面有什麼？', en: 'Dig in the sand!', strokes: 6, loopSfx: 'dig', reveal: 'shell', sfx: 'shell'),
        const TapStep(['ball'], say: '踢球！踢進去了！', en: 'Kick the ball!', tapSfx: 'ball_kick', sfx: 'yay', mood: Mood.happy),
      ],
    Task.tidy => _toys(big),
    Task.chore => planChore(chore, level: level, family: family),
    Task.bath => [
        const TapStep(['tap_off'], result: 'tap_on', say: '放水囉。', en: 'Run the water.', tapSfx: 'water_on', sfx: 'pour'),
        ChooseStep(
          options: const [Choice('temp_hot', '太燙', en: 'too hot'), Choice('temp_warm', '剛剛好', en: 'just right'), Choice('temp_cold', '太冷', en: 'too cold')],
          good: const {'temp_warm'},
          say: '試試水溫，哪一個剛剛好？',
          en: 'Which water is just right?',
          whyWrong: (p) => p == 'temp_hot' ? '燙燙！會縮手，太燙了。' : '冷冷的，會發抖。',
          sfx: 'splash',
        ),
        const ScrubStep(base: '@avatar', tool: 'soap', dirt: 'bubble', say: '搓泡泡，洗洗頭、洗洗身體。', en: 'Soap up: hair and body.', strokes: 10, loopSfx: 'bubble', sfx: 'splash'),
        const TapStep(['tap_on'], result: 'tap_off', say: '沖乾淨，關水。', en: 'Rinse and turn the water off.', tapSfx: 'splash', sfx: 'water_off'),
        const TapStep(['towel'], say: '擦乾乾。', en: 'Dry off.', tapSfx: 'towel', sfx: 'towel'),
        const ScrubStep(base: '@head', tool: 'hairdryer', say: '吹頭髮，呼～', en: 'Dry your hair.', strokes: 6, loopSfx: 'hairdryer', sfx: 'yay'),
        if (big) const TapStep(['lotion'], say: '擦乳液，皮膚香香。', en: 'Lotion on.', tapSfx: 'lotion', sfx: 'yay'),
      ],
    Task.sleep => [
        const TapStep(['curtain_open'], result: 'curtain_closed', say: '拉上窗簾。', en: 'Close the curtains.', tapSfx: 'curtain', sfx: 'curtain'),
        const TapStep(['bedroom/nightlight_on'], result: 'bedroom/nightlight_off', say: '關燈，喀。', en: 'Lights off.', tapSfx: 'light_off', sfx: 'light_off'),
        const TapStep(['blanket'], say: '蓋好被子。', en: 'Tuck in.', tapSfx: 'blanket', sfx: 'blanket', mood: Mood.sleepy),
        TapStep(const ['book_open'], say: stories[rnd.nextInt(stories.length)], en: 'A bedtime story.', tapSfx: 'book_open', sfx: 'yay', mood: Mood.sleepy),
        const TapStep(['@avatar'], say: '晚安，明天見。', en: 'Good night!', tapSfx: 'snore', sfx: 'night', mood: Mood.sleepy),
      ],
    Task.nap => const [
        TapStep(['curtain_open'], result: 'curtain_closed', say: '拉上窗簾，房間暗暗的。', en: 'Close the curtains.', tapSfx: 'curtain', sfx: 'curtain'),
        TapStep(['blanket'], say: '蓋好被子。', en: 'Tuck in.', tapSfx: 'blanket', sfx: 'blanket', mood: Mood.sleepy),
        HoldStep(prop: '@avatar', say: '閉上眼睛，睡一下下。', en: 'Close your eyes.', seconds: 3, loopSfx: 'snore', sfx: 'yawn', mood: Mood.sleepy),
      ],
    Task.market => _market(big, rnd),
    Task.cook => [
        const ScrubStep(base: 'food_carrot', tool: 'bubble', dirt: 'stain', say: '先把菜洗乾淨。', en: 'Wash the vegetables.', strokes: 6, loopSfx: 'water_on', sfx: 'water_off'),
        const DragStep(
          items: [DragItem('food_carrot', zh: '紅蘿蔔'), DragItem('food_meat', zh: '肉'), DragItem('food_egg', zh: '蛋')],
          slots: [DragSlot('pot', prop: 'pot', zh: '鍋子', capacity: 3)],
          say: '放進鍋子裡。',
          en: 'Into the pot.',
          dropSfx: 'pour',
        ),
        const ScrubStep(base: 'pot', tool: 'spoon', say: '攪一攪，香香的！', en: 'Stir it!', strokes: 6, loopSfx: 'spoon', sfx: 'yum', safety: Safety.hotPot),
        ..._eat(big),
      ],
  };
}

/// The steps for a chore (docs/design.md 「幫忙做家事」).
List<Step> planChore(Chore chore, {required Level level, int family = 3}) {
  final big = level == Level.big;
  return switch (chore) {
    Chore.toys => _toys(big),
    Chore.table => [_setTable(family)],
    Chore.wipe => const [ScrubStep(base: 'table_top', tool: 'rag', dirt: 'stain', say: '抹布擦一擦，桌子亮晶晶。', en: 'Wipe the table.', strokes: 8, loopSfx: 'wipe', sfx: 'yay')],
    Chore.laundry => [
        DragStep(
          items: [
            const DragItem('sock_1_a', slot: 'p1', zh: '襪子'),
            const DragItem('sock_1_b', slot: 'p1', zh: '襪子'),
            const DragItem('sock_2_a', slot: 'p2', zh: '襪子'),
            const DragItem('sock_2_b', slot: 'p2', zh: '襪子'),
            if (big) ...const [DragItem('sock_3_a', slot: 'p3', zh: '襪子'), DragItem('sock_3_b', slot: 'p3', zh: '襪子')],
          ],
          slots: [const DragSlot('p1', zh: '一雙', capacity: 2), const DragSlot('p2', zh: '一雙', capacity: 2), if (big) const DragSlot('p3', zh: '一雙', capacity: 2)],
          say: '收衣服！一樣的襪子放在一起。',
          en: 'Match the socks.',
          dropSfx: 'cloth',
          wrong: '這兩隻不一樣喔。',
        ),
        if (big) const TapStep(['peg', 'peg', 'peg'], say: '衣服夾到架上，夾緊緊。', en: 'Peg the shirts up.', tapSfx: 'peg', sfx: 'yay'),
      ],
    Chore.water => const [
        ChooseStep(
          options: [Choice('plant', '盆栽', en: 'plant'), Choice('plant_wilt', '枯掉的盆栽', en: 'wilted plant'), Choice('plant', '盆栽', en: 'plant')],
          good: {'plant_wilt'},
          say: '哪一盆渴了、垂下來了？',
          en: 'Which plant is thirsty?',
          sfx: 'pop',
        ),
        HoldStep(prop: 'watering_can', say: '按著澆水，剛剛好就放開。', en: 'Hold to water; let go when it is enough.', seconds: 2, tooLong: 4, loopSfx: 'watering', result: 'plant', tooMuch: '太多了，水滿出來了！再來一次。', sfx: 'grow'),
      ],
    Chore.feed => const [
        DragStep(items: [DragItem('kibble_bag', slot: 'bowl', zh: '飼料')], slots: [DragSlot('bowl', prop: 'buddy_bowl', zh: '碗')], say: '倒飼料給小夥伴。', en: 'Pour the kibble.', dropSfx: 'feed'),
        TapStep(['cup_water_full'], result: 'cup_water', say: '換乾淨的水。', en: 'Fresh water too.', tapSfx: 'pour', sfx: 'buddy_happy'),
      ],
    Chore.trash => [
        const TapStep(['garbage_truck'], say: '垃圾車的音樂來了！', en: 'The garbage truck!', tapSfx: 'garbage_truck', sfx: 'pop'),
        DragStep(
          items: [
            const DragItem('trash_bag', slot: 'bin_trash', zh: '垃圾'),
            const DragItem('recycle_bottle', slot: 'bin_bottle', zh: '瓶子'),
            if (big) ...const [DragItem('recycle_paper', slot: 'bin_paper', zh: '紙'), DragItem('recycle_food', slot: 'bin_food', zh: '廚餘')],
          ],
          slots: [
            const DragSlot('bin_trash', prop: 'bin_trash', zh: '垃圾桶'),
            const DragSlot('bin_bottle', prop: 'bin_bottle', zh: '回收瓶子'),
            if (big) ...const [DragSlot('bin_paper', prop: 'bin_paper', zh: '回收紙'), DragSlot('bin_food', prop: 'bin_food', zh: '廚餘')],
          ],
          say: '垃圾和回收分開放。',
          en: 'Sort the trash and recycling.',
          dropSfx: 'trash',
          wrong: '這個要放別的桶子喔。',
        ),
      ],
    Chore.sweep => const [
        ScrubStep(base: null, tool: 'broom', dirt: 'crumbs', say: '掃把掃一掃，把紙屑掃起來。', en: 'Sweep up the crumbs.', strokes: 8, loopSfx: 'broom', sfx: 'dustpan'),
        TapStep(['dustpan'], say: '倒進畚箕，乾淨了！', en: 'Into the dustpan!', tapSfx: 'dustpan', sfx: 'yay'),
      ],
  };
}

/// The steps for something that happened (docs/design.md 「偶爾會發生的事」).
List<Step> planHappening(Happening h, {required Level level, required math.Random rnd}) {
  final big = level == Level.big;
  return switch (h) {
    Happening.pee => _toilet(big),
    Happening.hungry => const [TapStep(['kitchen/fridge'], say: '打開冰箱，拿一個蘋果。', en: 'An apple from the fridge.', tapSfx: 'door', sfx: 'pop'), TapStep(['food_apple', 'food_apple'], say: '咬一口，脆脆的！', en: 'Crunch!', tapSfx: 'chew', sfx: 'yum', mood: Mood.happy)],
    Happening.sleepy => const [TapStep(['blanket'], say: '好想睡，躺一下下。', en: 'Lie down a little.', tapSfx: 'blanket', sfx: 'snore', mood: Mood.sleepy), HoldStep(prop: '@avatar', say: '閉上眼睛休息一下。', en: 'Rest your eyes.', seconds: 2, loopSfx: 'snore', sfx: 'yawn', mood: Mood.sleepy)],
    Happening.thirsty => const [TapStep(['cup_water'], result: 'cup_water_full', say: '裝一杯水。', en: 'Fill a cup.', tapSfx: 'pour', sfx: 'pop'), _drink],
    Happening.sweaty => const [TapStep(['towel'], say: '擦擦汗。', en: 'Wipe the sweat.', tapSfx: 'towel', sfx: 'towel'), _drink],
    Happening.cold => const [DragStep(board: '@avatar', items: [DragItem('cloth_jacket', slot: 'body', zh: '外套')], slots: [DragSlot('body', zh: '身體', x: 0.5, y: 0.6)], say: '冷冷的，穿上外套。', en: 'Put on a jacket.', dropSfx: 'zipper', mood: Mood.sad)],
    Happening.sneeze => [
        const TapStep(['tissue'], say: '哈啾！擦擦鼻涕。', en: 'Achoo! Wipe your nose.', tapSfx: 'tissue', sfx: 'pop', mood: Mood.sick),
        _drink,
        ..._clinic(big),
      ],
    Happening.fall => const [
        TapStep(['tap_off'], result: 'tap_on', say: '跌倒了，先把傷口洗乾淨。', en: 'Wash the scrape.', tapSfx: 'water_on', sfx: 'water_off', mood: Mood.sad),
        TapStep(['bandage'], say: '貼上 OK 繃。', en: 'A bandage.', tapSfx: 'bandage', sfx: 'pop'),
        TapStep(['@avatar'], say: '秀秀，不痛了！', en: 'All better!', tapSfx: 'tap', sfx: 'yay', mood: Mood.happy),
      ],
    Happening.mosquito => const [
        TapStep(['mosquito'], say: '蚊子！趕走牠。', en: 'Shoo, mosquito!', tapSfx: 'mosquito', sfx: 'pop'),
        TapStep(['medicine'], say: '癢癢的，擦藥，不要抓喔。', en: 'Put on cream, do not scratch.', tapSfx: 'lotion', sfx: 'yay'),
      ],
    Happening.doorbell => [
        const TapStep(['entrance/door'], say: '叮咚！誰來了？開門看看。', en: 'Ding-dong! Who is it?', tapSfx: 'door', sfx: 'pop'),
        if (rnd.nextBool())
          const TapStep(['grandma'], say: '阿嬤來了！說「阿嬤好！」', en: 'Grandma! Say hello!', tapSfx: 'bye', sfx: 'yay', mood: Mood.happy)
        else
          const TapStep(['package'], say: '郵差叔叔送包裹來，說「謝謝！」', en: 'The mail carrier! Say thank you!', tapSfx: 'bye', sfx: 'yay', mood: Mood.happy),
      ],
    Happening.phone => const [
        TapStep(['living/phone'], say: '鈴鈴鈴！接電話：「喂，阿公好！」', en: 'Ring ring! Hello, Grandpa!', tapSfx: 'phone_ring', sfx: 'pop', mood: Mood.happy),
        TapStep(['living/phone'], say: '「阿公再見！」把電話放好。', en: 'Bye, Grandpa!', tapSfx: 'bye', sfx: 'yay'),
      ],
    Happening.blackout => const [TapStep(['flashlight'], say: '停電了，黑黑的。找到手電筒，不怕！', en: 'The lights went out. Find the torch!', tapSfx: 'flashlight', sfx: 'light_on', mood: Mood.sad)],
    Happening.garbage => planChore(Chore.trash, level: level),
    Happening.buddyHungry => planChore(Chore.feed, level: level),
    Happening.plant => planChore(Chore.water, level: level),
    Happening.rainLaundry => const [
        DragStep(
          items: [DragItem('shirt_hanging', zh: '衣服'), DragItem('shirt_hanging', zh: '衣服')],
          slots: [DragSlot('basket', prop: 'basket', zh: '籃子', capacity: 2)],
          say: '下雨了！快把衣服收進來。',
          en: 'Rain! Bring in the laundry!',
          dropSfx: 'cloth',
        ),
      ],
    Happening.thunder => const [TapStep(['@buddy'], say: '轟隆隆，打雷了。抱抱小夥伴，不怕不怕。', en: 'Thunder! Hug your buddy.', tapSfx: 'buddy_happy', sfx: 'yay', mood: Mood.sad, safety: Safety.thunder)],
    Happening.earthquake => const [
        DragStep(
          items: [DragItem('@avatar', slot: 'table', zh: '我')],
          slots: [DragSlot('table', prop: 'table_hide', zh: '桌子下面')],
          say: '地震！躲到桌子下面，保護頭！',
          en: 'Earthquake! Under the table, cover your head!',
          dropSfx: 'pop',
          mood: Mood.sad,
          safety: Safety.quake,
        ),
        HoldStep(prop: 'table_hide', say: '按著，等地震停下來……停了！', en: 'Hold on until it stops.', seconds: 3, loopSfx: 'earthquake', sfx: 'yay'),
      ],
    Happening.share => const [
        TapStep(['toy_car'], say: '小夥伴也想玩。先給牠玩一下，輪流！', en: 'Take turns: buddy first.', tapSfx: 'share', sfx: 'buddy_happy'),
        TapStep(['toy_block'], say: '你先玩積木，等一下換你玩車車。', en: 'You play blocks, then swap.', tapSfx: 'toy_drop', sfx: 'yay', mood: Mood.happy),
      ],
    Happening.angry => const [
        TapStep(['breath_1', 'breath_2', 'breath_3'], say: '好生氣！深呼吸三次：一、二、三。', en: 'Angry? Breathe: one, two, three.', tapSfx: 'deep_breath', sfx: 'yay', mood: Mood.sad),
        TapStep(['@avatar'], say: '好多了，再試一次！', en: 'Better. Try again!', tapSfx: 'tap', sfx: 'yay', mood: Mood.happy),
      ],
    Happening.spill => const [
        TapStep(['@buddy'], say: '牛奶打翻了。說「對不起」，沒關係。', en: 'Spilled! Say sorry.', tapSfx: 'spill', sfx: 'pop', mood: Mood.sad),
        ScrubStep(base: 'table_top', tool: 'rag', dirt: 'stain', say: '一起擦乾淨。', en: 'Wipe it up together.', strokes: 6, loopSfx: 'wipe', sfx: 'yay'),
      ],
    Happening.classmate => const [
        TapStep(['tissue'], say: '同學哭了。遞一張衛生紙。', en: 'A tissue for your friend.', tapSfx: 'tissue', sfx: 'pop', mood: Mood.sad),
        TapStep(['classmate_1'], say: '拍拍，沒事了。', en: 'There, there.', tapSfx: 'tap', sfx: 'yay', mood: Mood.happy),
      ],
  };
}

// ---------------------------------------------------------------- pieces

const _drink = TapStep(['cup_water_full'], result: 'cup_water', say: '咕嚕咕嚕，喝水。', en: 'Drink some water.', tapSfx: 'drink', sfx: 'yay');

List<Step> _teeth(bool big) => [
      const DragStep(items: [DragItem('toothpaste', slot: 'brush', zh: '牙膏')], slots: [DragSlot('brush', prop: 'toothbrush', zh: '牙刷')], say: '擠牙膏到牙刷上。', en: 'Toothpaste on the brush.', dropSfx: 'toothpaste'),
      ScrubStep(base: 'mouth_big', tool: 'toothbrush', dirt: 'dirt', say: big ? '刷刷刷，上面、下面、裡面都要刷。' : '刷刷刷，牙齒刷乾淨。', en: 'Brush: top, bottom, inside.', strokes: big ? 12 : 8, loopSfx: 'brush', mood: Mood.mouth, sfx: 'yay'),
      const TapStep(['cup'], say: '漱口，噗～', en: 'Rinse and spit!', tapSfx: 'rinse', sfx: 'yay', mood: Mood.mouth),
    ];

List<Step> _face() => const [
      TapStep(['tap_off'], result: 'tap_on', say: '開水，洗洗臉。', en: 'Water on, wash your face.', tapSfx: 'water_on', sfx: 'pop'),
      ScrubStep(base: '@head', tool: 'towel', say: '擦擦臉，亮晶晶。', en: 'Pat your face dry.', strokes: 5, loopSfx: 'rub', sfx: 'water_off'),
    ];

List<Step> _handwash(bool big) => [
      if (big) const TapStep(['tap_off'], result: 'tap_on', say: '開水，手沖濕。', en: 'Water on.', tapSfx: 'water_on', sfx: 'pop'),
      const TapStep(['soap'], say: '壓一下洗手乳。', en: 'A pump of soap.', tapSfx: 'soap', sfx: 'pop'),
      ScrubStep(base: 'hands', tool: 'bubble', dirt: 'dirt', say: big ? '搓搓搓：手心、手背、指縫。' : '搓搓搓，泡泡多多。', en: 'Rub: palms, backs, between fingers.', strokes: big ? 10 : 6, loopSfx: 'rub', sfx: 'splash'),
      const TapStep(['tap_on'], result: 'tap_off', say: '沖乾淨，關水，省水。', en: 'Rinse, water off.', tapSfx: 'splash', sfx: 'water_off'),
      const TapStep(['towel'], say: '擦乾乾。', en: 'Dry your hands.', tapSfx: 'towel', sfx: 'yay'),
    ];

List<Step> _toilet(bool big) => [
      const TapStep(['toilet_closed'], result: 'toilet_open', say: '打開馬桶蓋，脫褲子坐好。', en: 'Lid up, sit down.', tapSfx: 'tap', sfx: 'pop', mood: Mood.squirm),
      const HoldStep(prop: 'toilet_open', say: '坐一下，哼哼歌，等一等。', en: 'Sit, hum a tune, wait.', seconds: 3, loopSfx: 'hum', sfx: 'pop'),
      const TapStep(['paper'], say: '擦屁屁。', en: 'Wipe.', tapSfx: 'paper', sfx: 'pop'),
      const TapStep(['flush'], say: '拉褲子，沖水！', en: 'Pants up, flush!', tapSfx: 'toilet_flush', sfx: 'yay', mood: Mood.happy),
      ..._handwash(big),
    ];

List<Step> _dress(Weather w, bool big) {
  final top = switch (w) { Weather.cold => 'cloth_jacket', Weather.rain || Weather.storm => 'cloth_raincoat', _ => 'cloth_tshirt' };
  final bottom = w == Weather.hot || w == Weather.sun ? 'cloth_shorts' : 'cloth_pants';
  return [
    ChooseStep(
      options: const [Choice('cloth_tshirt', '短袖', en: 't-shirt'), Choice('cloth_jacket', '外套', en: 'jacket'), Choice('cloth_raincoat', '雨衣', en: 'raincoat')],
      good: {top},
      say: '看看窗外，今天${w.zh}。要穿哪一件？',
      en: 'It is ${w.en} today. Which one?',
      whyWrong: (p) => switch (w) {
        Weather.cold => '穿這件會冷得發抖喔，換一件。',
        Weather.hot || Weather.sun => '穿這件會流汗喔，換一件。',
        _ => '下雨穿雨衣才不會濕喔。',
      },
      sfx: 'cloth',
    ),
    DragStep(
      board: '@avatar',
      items: [DragItem(top, slot: 'body', zh: '上衣'), DragItem(bottom, slot: 'legs', zh: bottom == 'cloth_shorts' ? '短褲' : '長褲')],
      slots: const [DragSlot('body', zh: '身體', x: 0.5, y: 0.55), DragSlot('legs', zh: '腿', x: 0.5, y: 0.82)],
      say: '衣服拖到身上穿好。',
      en: 'Put the clothes on.',
      dropSfx: 'cloth',
      wrong: '這件要穿在另一邊喔。',
    ),
    if (big) const TapStep(['button', 'button', 'button'], say: '扣釦子，一顆、兩顆、三顆。', en: 'Buttons: one, two, three.', tapSfx: 'button', sfx: 'zipper'),
  ];
}

DragStep _setTable(int family) => DragStep(
      board: 'kitchen/table',
      items: [for (var i = 0; i < family; i++) const DragItem('bowl', zh: '碗'), for (var i = 0; i < family; i++) const DragItem('chopsticks', zh: '筷子')],
      slots: [for (var i = 0; i < family; i++) DragSlot('seat_$i', zh: '位子', capacity: 2, x: (i + 0.5) / family, y: 0.5)],
      say: '擺碗筷：$family個人，$family個碗、$family雙筷子，數一數。',
      en: 'Set the table: $family bowls, $family pairs of chopsticks.',
      dropSfx: 'dishes',
    );

List<Step> _eat(bool big) => [
      const DragStep(
        board: 'plate',
        items: [DragItem('food_rice', slot: 'rice', zh: '飯'), DragItem('food_veg', slot: 'veg', zh: '菜'), DragItem('food_meat', slot: 'meat', zh: '肉'), DragItem('food_fruit', slot: 'fruit', zh: '水果')],
        slots: [DragSlot('rice', zh: '飯', x: 0.3, y: 0.3), DragSlot('veg', zh: '菜', x: 0.7, y: 0.3), DragSlot('meat', zh: '肉', x: 0.3, y: 0.7), DragSlot('fruit', zh: '水果', x: 0.7, y: 0.7)],
        say: '飯、菜、肉、水果，都放到盤子上，每樣都吃才會長大。',
        en: 'Rice, veggies, meat and fruit on the plate.',
        dropSfx: 'pop',
        wrong: '放到它自己的格子裡。',
      ),
      TapStep(List.filled(big ? 4 : 3, 'spoon'), say: '啊～嗯，好吃！', en: 'Yum!', tapSfx: 'chew', sfx: 'yum', mood: Mood.mouth),
      _drink,
      const TapStep(['towel'], say: '擦擦嘴。', en: 'Wipe your mouth.', tapSfx: 'towel', sfx: 'yay', mood: Mood.happy),
    ];

List<Step> _toys(bool big) => [
      DragStep(
        items: [
          const DragItem('toy_car', slot: 'box_car', zh: '車車'),
          const DragItem('toy_block', slot: 'box_block', zh: '積木'),
          const DragItem('toy_doll', slot: 'box_doll', zh: '娃娃'),
          if (big) ...const [DragItem('toy_ball', slot: 'box_car', zh: '球'), DragItem('toy_block', slot: 'box_block', zh: '積木'), DragItem('toy_doll', slot: 'box_doll', zh: '娃娃')],
        ],
        slots: [DragSlot('box_car', prop: 'box_car', zh: '車車的箱子', capacity: big ? 2 : 1), DragSlot('box_block', prop: 'box_block', zh: '積木的箱子', capacity: big ? 2 : 1), DragSlot('box_doll', prop: 'box_doll', zh: '娃娃的箱子', capacity: big ? 2 : 1)],
        say: '收玩具！車車、積木、娃娃，各自回家。',
        en: 'Tidy up: cars, blocks, dolls in their boxes.',
        dropSfx: 'toy_drop',
        wrong: '看看箱子上的圖，是這個箱子嗎？',
      ),
    ];

const shopFoods = ['food_apple', 'food_banana', 'food_carrot', 'food_milk', 'food_egg', 'food_fish'];
const shopNames = {'food_apple': '蘋果', 'food_banana': '香蕉', 'food_carrot': '紅蘿蔔', 'food_milk': '牛奶', 'food_egg': '蛋', 'food_fish': '魚'};

List<Step> _market(bool big, math.Random rnd) {
  final foods = [...shopFoods]..shuffle(rnd);
  final wanted = foods.sublist(0, 3);
  final onShelf = foods.sublist(0, big ? 6 : 4)..shuffle(rnd);
  return [
    const TapStep(['cart'], say: '推推車，我們來買菜。', en: 'Push the cart!', tapSfx: 'cart', sfx: 'pop'),
    DragStep(
      board: 'list',
      items: [for (final f in onShelf) DragItem(f, zh: shopNames[f])],
      slots: [DragSlot('cart', prop: 'cart', zh: '推車', capacity: 3, accepts: wanted.toSet())],
      say: '照清單找：${wanted.map((f) => shopNames[f]).join('、')}。',
      en: 'Find what is on the list.',
      dropSfx: 'cart',
      wrong: '清單上沒有這個喔。',
    ),
    const TapStep(['cashier'], say: '排隊付錢，嗶嗶。', en: 'Line up and pay.', tapSfx: 'scan', sfx: 'coins'),
    DragStep(
      items: [for (final f in wanted) DragItem(f, zh: shopNames[f])],
      slots: const [DragSlot('bag', prop: 'bag_shop', zh: '袋子', capacity: 3)],
      say: '放進袋子，帶回家。',
      en: 'Into the bag!',
      dropSfx: 'bag_rustle',
    ),
  ];
}

List<Step> _clinic(bool big) => [
      const TapStep(['thermometer'], say: '去診所。先量體溫，嗶嗶。', en: 'At the clinic: temperature first.', tapSfx: 'thermometer', sfx: 'pop', mood: Mood.sick),
      const TapStep(['doctor'], say: '張開嘴巴，啊～醫生看喉嚨。', en: 'Say ahh!', tapSfx: 'ahh', sfx: 'pop', mood: Mood.mouth),
      const TapStep(['stethoscope', 'stethoscope'], say: '聽診器涼涼的，聽心跳，咚咚。', en: 'The stethoscope listens.', tapSfx: 'heartbeat', sfx: 'pop'),
      const HoldStep(prop: 'breath_2', say: '要打針了，深呼吸，一、二、三。', en: 'A shot: deep breath, one, two, three.', seconds: 3, loopSfx: 'deep_breath', sfx: 'poke'),
      const TapStep(['medicine'], say: '一下下就好了！拿藥回家。', en: 'All done! Medicine to go.', tapSfx: 'medicine', sfx: 'pop', mood: Mood.happy),
      const TapStep(['sticker_brave'], say: '你好勇敢，貼一張勇敢貼紙！', en: 'So brave! A sticker!', tapSfx: 'sticker', sfx: 'brave', mood: Mood.happy),
    ];

/// Every prop name the steps can ask for (test/art_test.dart checks the
/// pictures exist).
Set<String> allStepProps() {
  final names = <String>{};
  void add(Step s) {
    switch (s) {
      case TapStep(:final props, :final result):
        names.addAll(props);
        if (result != null) names.add(result);
      case ScrubStep(:final base, :final tool, :final dirt, :final reveal):
        names.addAll([?base, tool, ?dirt, ?reveal]);
      case DragStep(:final items, :final slots, :final board):
        names.addAll([for (final i in items) i.prop, for (final s in slots) ?s.prop, ?board]);
      case ChooseStep(:final options):
        names.addAll([for (final o in options) o.prop]);
      case HoldStep(:final prop, :final result):
        names.addAll([prop, ?result]);
    }
  }

  final rnd = math.Random(1);
  for (final t in Task.values) {
    for (final l in Level.values) {
      for (final w in Weather.values) {
        for (final c in Chore.values) {
          planTask(t, level: l, weather: w, chore: c, rnd: rnd).forEach(add);
        }
      }
    }
  }
  for (final h in Happening.values) {
    for (final l in Level.values) {
      for (var i = 0; i < 4; i++) {
        planHappening(h, level: l, rnd: rnd).forEach(add);
      }
    }
  }
  return names..removeWhere((n) => n.startsWith('@'));
}
