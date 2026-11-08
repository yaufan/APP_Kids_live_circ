// Records a demo video of 小小生活家 being played: a scripted child (a white
// dot where the finger is) with a caption under the phone screen; the music
// and sounds the app asked for are written down and mixed in afterwards by
// tools/demo_audio.py.
//
//   flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true
//   python3 ../tools/demo_audio.py
//
// Needs ffmpeg; writes build/demo/demo.mp4, chapters.txt and sounds.txt.
// Skipped in normal test runs.
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/material.dart' hide Step;
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/app/app.dart';
import 'package:little_life/app/strings.dart';
import 'package:little_life/core/content.dart';
import 'package:little_life/core/game.dart';
import 'package:little_life/core/providers.dart';
import 'package:little_life/core/sounds.dart';
import 'package:little_life/core/store.dart';
import 'package:little_life/core/voice.dart';
import 'package:little_life/features/parent/parent_gate.dart';
import 'package:little_life/features/play/play_screen.dart';
import 'package:little_life/features/play/step_views.dart';

import '../helpers.dart' show loadFonts;

const _phone = Size(390, 844);
const _captionHeight = 84.0;
const _fps = 10;
const _demo = bool.fromEnvironment('DEMO');

/// The music and the sounds asked for, with the frame they were asked at.
class _Recording implements Sounds {
  _Recording(this.frame);

  final int Function() frame;
  final lines = <String>[];
  final _holders = MusicHolders();
  Music? _playing;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => lines.add('${frame()} sfx $sfx');

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _changed();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _changed();
  }

  void _changed() {
    final now = _holders.current;
    if (now == _playing) return;
    _playing = now;
    lines.add('${frame()} music ${now?.file ?? '-'}');
  }
}

void main() {
  testWidgets('demo video', skip: !_demo, (tester) async {
    await tester.runAsync(loadFonts);
    tester.view.physicalSize = Size(_phone.width * 3, (_phone.height + _captionHeight) * 3);
    tester.view.devicePixelRatio = 3;
    addTearDown(tester.view.reset);

    var frameCount = 0;
    var now = DateTime(2026, 11, 8, 10);
    final track = _Recording(() => frameCount);
    final finger = ValueNotifier<Offset?>(null);
    final caption = ValueNotifier<String>('');
    final key = GlobalKey();
    final store = MemoryStore();
    await tester.pumpWidget(RepaintBoundary(
      key: key,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(children: [
          SizedBox.fromSize(
            size: _phone,
            child: MediaQuery(
              data: const MediaQueryData(size: _phone, devicePixelRatio: 3, padding: EdgeInsets.only(top: 24)),
              child: Stack(children: [
                ProviderScope(
                  overrides: [
                    storeProvider.overrideWithValue(store),
                    savedGameProvider.overrideWithValue(const Game()),
                    soundsProvider.overrideWithValue(track),
                    voiceProvider.overrideWithValue(const SilentVoice()),
                    randomProvider.overrideWithValue(math.Random(5)),
                    clockProvider.overrideWithValue(() => now),
                  ],
                  child: const LittleLifeApp(),
                ),
                IgnorePointer(child: ValueListenableBuilder(valueListenable: finger, builder: (_, at, _) => _Finger(at))),
              ]),
            ),
          ),
          SizedBox(
            width: _phone.width,
            height: _captionHeight,
            child: ColoredBox(
              color: const Color(0xFFEF7B6B),
              child: Center(
                child: ValueListenableBuilder(
                  valueListenable: caption,
                  builder: (_, text, _) => Text(text, textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Huninn', color: Colors.white, fontSize: 17, height: 1.35)),
                ),
              ),
            ),
          ),
        ]),
      ),
    ));

    final rec = (await tester.runAsync(() => _Recorder.start(key)))!;
    final marks = <String>[];
    void mark(String name) => marks.add('$name $frameCount');
    Future<void> frames(int n) async {
      for (var i = 0; i < n; i++) {
        frameCount++;
        await tester.runAsync(() async {
          await rec.capture();
          await Future<void>.delayed(const Duration(milliseconds: 15));
        });
        await tester.pump(const Duration(milliseconds: 1000 ~/ _fps));
      }
    }

    Future<void> seconds(double s) => frames((s * _fps).round());
    Future<void> touch(Offset at) async {
      finger.value = at;
      await frames(2);
      await tester.tapAt(at);
      await frames(2);
      finger.value = null;
    }

    Offset at(String l) => tester.getCenter(find.bySemanticsLabel(l).last);
    Future<void> label(String l) async {
      final f = find.bySemanticsLabel(l);
      if (f.evaluate().isEmpty || !tester.getRect(f.last).overlaps(Offset.zero & _phone)) {
        await tester.scrollUntilVisible(f, 120, scrollable: find.byType(Scrollable).first);
        await frames(3);
      }
      await touch(at(l));
    }
    Future<void> thing(String id) => touch(tester.getCenter(find.byKey(ValueKey('thing-$id'))));
    Future<void> dragTo(Offset from, Offset to) async {
      finger.value = from;
      final g = await tester.startGesture(from);
      await frames(2);
      for (var i = 1; i <= 5; i++) {
        final p = Offset.lerp(from, to, i / 5)!;
        await g.moveTo(p);
        finger.value = p;
        await frames(1);
      }
      await g.up();
      finger.value = null;
      await frames(2);
    }

    ProviderContainer container() => ProviderScope.containerOf(tester.element(find.byType(LittleLifeApp)));
    void change(Game Function(Game) f) => container().read(gameProvider.notifier).change(f);

    /// Plays the little game on screen, step by step, the caption following.
    Future<void> playGame({String? firstCaption}) async {
      var guard = 0;
      var first = true;
      while (find.byType(PlayScreen).evaluate().isNotEmpty && guard++ < 30) {
        await frames(4);
        final tapView = find.byType(TapView), scrub = find.byType(ScrubView), drag = find.byType(DragView), choose = find.byType(ChooseView), hold = find.byType(HoldView);
        final bubble = find.byKey(find.byType(PlayScreen).evaluate().isEmpty ? const ValueKey('x') : const ValueKey('say-0'));
        if (first && firstCaption != null) {
          caption.value = firstCaption;
        } else {
          final say = tester.widgetList<Text>(find.descendant(of: find.byType(PlayScreen), matching: find.byType(Text))).map((t) => t.data ?? '').where((t) => t.length > 4).toList();
          if (say.isNotEmpty) caption.value = say.first;
        }
        first = false;
        bubble.evaluate();
        await seconds(1.2);
        if (tapView.evaluate().isNotEmpty) {
          final step = tester.widget<TapView>(tapView.last).step;
          final same = step.props.toSet().length == 1 && step.props.length > 1;
          for (var i = 0; i < step.props.length; i++) {
            final k = find.byKey(ValueKey('tap-${same ? math.min(i, step.props.length - 1) : i}'));
            if (k.evaluate().isEmpty) break;
            await touch(tester.getCenter(k.last));
            await seconds(0.4);
          }
        } else if (scrub.evaluate().isNotEmpty) {
          final box = tester.getRect(scrub.last);
          final side = math.min(box.width, box.height);
          final o = Offset(box.center.dx - side / 2, box.center.dy - side / 2);
          finger.value = o + Offset(side * 0.1, side * 0.2);
          final g = await tester.startGesture(finger.value!);
          for (var row = 0; row < 8; row++) {
            for (var col = 0; col <= 6; col++) {
              final x = row.isEven ? col / 6 : 1 - col / 6;
              final p = o + Offset(side * (0.08 + 0.84 * x), side * (0.15 + 0.7 * row / 7));
              await g.moveTo(p);
              finger.value = p;
              await frames(1);
            }
          }
          await g.up();
          finger.value = null;
        } else if (drag.evaluate().isNotEmpty) {
          final step = tester.widget<DragView>(drag.last).step;
          final filled = <String, int>{};
          for (var i = 0; i < step.items.length; i++) {
            final item = step.items[i];
            final slot = step.slots.where((s) => s.takes(item) && (filled[s.id] ?? 0) < s.capacity).firstOrNull;
            if (slot == null) continue;
            filled[slot.id] = (filled[slot.id] ?? 0) + 1;
            final from = find.byKey(ValueKey('item-$i')), to = find.byKey(ValueKey('slot-${slot.id}'));
            if (from.evaluate().isEmpty || to.evaluate().isEmpty) continue;
            await dragTo(tester.getCenter(from.last), tester.getCenter(to.last));
          }
        } else if (choose.evaluate().isNotEmpty) {
          final step = tester.widget<ChooseView>(choose.last).step;
          final wrong = step.options.indexWhere((o) => !step.good.contains(o.prop));
          if (wrong >= 0) {
            await touch(tester.getCenter(find.byKey(ValueKey('choice-$wrong')).last));
            await seconds(1.4);
          }
          final i = step.options.indexWhere((o) => step.good.contains(o.prop));
          await touch(tester.getCenter(find.byKey(ValueKey('choice-$i')).last));
        } else if (hold.evaluate().isNotEmpty) {
          final step = tester.widget<HoldView>(hold.last).step;
          final c = tester.getCenter(find.byKey(const ValueKey('hold')).last);
          finger.value = c;
          final g = await tester.startGesture(c);
          await seconds(step.seconds + 0.3);
          await g.up();
          finger.value = null;
        }
        await seconds(0.8);
      }
      await seconds(2.2);
    }

    // Setup.
    mark('setup');
    caption.value = '小小生活家：幫自己取名字、選角色\n和一隻小夥伴，一起過一天';
    await seconds(2.5);
    await tester.enterText(find.byKey(const ValueKey('name')), '小安');
    await frames(3);
    await label('頭髮 2');
    await seconds(0.6);
    await label('衣服 6');
    await seconds(0.6);
    caption.value = '小狗、小貓、小兔、小鴨，選一隻陪你';
    await label('選一隻小夥伴 rabbit');
    await seconds(1.5);
    await label(Strings.start);
    await seconds(1.5);

    // The living room and the clock.
    mark('living');
    caption.value = '一個畫面只有一個房間（手機好看好點）\n上面的時鐘指到太陽：該起床了！';
    await seconds(4);
    caption.value = '該去的房間會發亮：點它就走過去';
    await label('房間');
    await seconds(2.5);
    caption.value = '點發亮的床，開始「起床」的小遊戲';
    await thing('bed');
    await seconds(1);
    mark('wake');
    await playGame(firstCaption: '拉開窗簾、伸懶腰：每一步都是點一點');
    caption.value = '做完得到一張貼紙，時鐘指到下一件事';
    await seconds(2);

    // Teeth.
    mark('teeth');
    caption.value = '刷牙：往右走到廁所';
    await label('往右：廁所');
    await seconds(2);
    await thing('sink');
    await seconds(1);
    await playGame(firstCaption: '擠牙膏：拖到牙刷上');
    caption.value = '點房子裡的東西會念名字\n（家長可以加英文）';
    await thing('bathtub');
    await seconds(1.5);
    await thing('mirror');
    await seconds(1.5);

    // The clock.
    mark('clock');
    caption.value = '點時鐘：轉指針或點圖案，就換時段\n時鐘走遊戲的時間，不跟手機';
    await label(Strings.clockOpen);
    await seconds(3);
    await touch(at('${Strings.clockOpen} 上學'));
    await seconds(2);
    await label(Strings.back);
    await seconds(1.5);

    // Something happens.
    mark('happening');
    change((g) => g.copyWith(day: g.day!.copyWith(active: Happening.pee)));
    caption.value = '偶爾會發生的事：想尿尿了！\n夾腿、頭上一滴小水滴，要注意到牠';
    await seconds(3.5);
    await thing('toilet');
    await seconds(1);
    await playGame(firstCaption: '上廁所：打開馬桶蓋、坐好、哼歌等一下');

    // Out.
    mark('out');
    caption.value = '下樓、到門口、出門';
    await label('下樓：客廳');
    await seconds(1.5);
    await label('往右：門口');
    await seconds(1.5);
    await label('出門：小街');
    await seconds(1.5);
    caption.value = '小街：公園、幼兒園、超市、診所';
    await seconds(2.5);
    change((g) => g.turnClock(g.day!.plan(g.settings).indexOf(Task.park)));
    await thing('park');
    await seconds(2);
    caption.value = '公園：先過馬路（紅燈停、綠燈行）\n再溜滑梯、盪鞦韆、挖沙、踢球';
    await thing('slide');
    await seconds(1);
    mark('park');
    await playGame(firstCaption: '紅燈：按著等一下');

    // Stickers.
    mark('stickers');
    caption.value = '貼紙表：今天做完的事、家裡的裝飾、身高尺';
    await label(Strings.stickers);
    await seconds(3.5);
    await label(Strings.back);
    await seconds(1);

    // Bedtime.
    mark('sleep');
    change((g) => g.turnClock(g.day!.plan(g.settings).indexOf(Task.sleep)));
    caption.value = '回家，上樓去房間睡覺';
    await label('回小街：小街');
    await seconds(1.2);
    await label(Strings.home);
    await seconds(1.2);
    await label('往左：客廳');
    await seconds(1.2);
    await label('上樓：房間');
    await seconds(1.5);
    await thing('bed');
    await seconds(1);
    await playGame(firstCaption: '拉上窗簾、關燈、蓋被子、聽一段小故事');
    caption.value = '晚安！整個家一間一間變暗\n一天全部做完，家裡多一樣裝飾';
    await seconds(4.5);
    await touch(tester.getCenter(find.byKey(const ValueKey('night'))));
    await seconds(2.5);

    // Rest.
    mark('rest');
    now = now.add(const Duration(minutes: 15, seconds: 1));
    caption.value = '家長設定的時間到了（預設 15 分鐘）\n小角色睡著了：換你去做了！';
    await seconds(5.5);

    // Parent mode.
    mark('parent');
    caption.value = '家長答對題目，才能再玩或進家長模式';
    const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    Future<void> gate() async {
      final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
      for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
        await touch(tester.getCenter(find.byKey(ValueKey('gate-key-$d'))));
        await frames(3);
      }
    }

    await label(Strings.parent);
    await seconds(1.2);
    await gate();
    await seconds(1.5);
    await label(Strings.parent);
    await seconds(1);
    await gate();
    await seconds(1);
    caption.value = '家長模式：年齡、每次玩多久\n一天要做哪些事、聲音、最近幾天做完哪些';
    await seconds(3);
    await tester.drag(find.byType(ListView), const Offset(0, -900));
    await seconds(3);
    caption.value = '';
    mark('end');
    await seconds(0.5);

    expect(ParentPass.take(), isFalse);
    await tester.runAsync(() async {
      await rec.finish();
      File('build/demo/chapters.txt').writeAsStringSync('${marks.join('\n')}\n');
      File('build/demo/sounds.txt').writeAsStringSync('fps $_fps\nframes $frameCount\n${track.lines.join('\n')}\n');
    });
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }, timeout: const Timeout(Duration(minutes: 40)));
}

class _Finger extends StatelessWidget {
  const _Finger(this.at);

  final Offset? at;

  @override
  Widget build(BuildContext context) {
    final p = at;
    if (p == null) return const SizedBox.expand();
    return Stack(children: [
      Positioned(
        left: p.dx - 22,
        top: p.dy - 22,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.55),
            border: Border.all(color: const Color(0xFF4A3B32).withValues(alpha: 0.5), width: 3),
          ),
        ),
      ),
    ]);
  }
}

/// Streams frames of [key]'s boundary into ffmpeg.
class _Recorder {
  _Recorder(this._key, this._ffmpeg);

  final GlobalKey _key;
  final Process _ffmpeg;

  static Future<_Recorder> start(GlobalKey key) async {
    Directory('build/demo').createSync(recursive: true);
    final size = Size(_phone.width * 2, (_phone.height + _captionHeight) * 2);
    final ffmpeg = await Process.start('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '${size.width.toInt()}x${size.height.toInt()}', '-r', '$_fps', '-i', '-',
      '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', 'build/demo/demo_silent.mp4',
    ]);
    ffmpeg.stderr.listen(stderr.add);
    return _Recorder(key, ffmpeg);
  }

  Future<void> capture() async {
    final boundary = _key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    image.dispose();
    _ffmpeg.stdin.add(bytes!.buffer.asUint8List());
    await _ffmpeg.stdin.flush();
  }

  Future<void> finish() async {
    await _ffmpeg.stdin.flush();
    await _ffmpeg.stdin.close();
    final code = await _ffmpeg.exitCode;
    if (code != 0) throw StateError('ffmpeg failed ($code)');
  }
}
