import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/scenes.dart';

/// The first start (and 「重新選角色」 from parent mode): a grown-up may type
/// a name; the child taps a hair, a skin, a shirt and a buddy
/// (docs/design.md 「取名字、選角色」). Everything is a picture; nothing to read.
class SetupScreen extends ConsumerStatefulWidget {
  const SetupScreen({super.key});

  @override
  ConsumerState<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends ConsumerState<SetupScreen> {
  late final TextEditingController _name;
  late Avatar _avatar;
  late Buddy _buddy;

  @override
  void initState() {
    super.initState();
    final p = ref.read(gameProvider).profile;
    _name = TextEditingController(text: p == null ? '' : p.name);
    _avatar = p?.avatar ?? const Avatar();
    _buddy = p?.buddy ?? Buddy.dog;
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  void _start() {
    final name = _name.text.trim();
    final profile = Profile(name: name.isEmpty ? Profile.defaultName : (name.length > Profile.maxName ? name.substring(0, Profile.maxName) : name), avatar: _avatar, buddy: _buddy);
    ref.read(gameProvider.notifier).setProfile(profile);
    ref.read(soundsProvider).play(_buddy.sound);
    speak(ref, Strings.welcome(profile.name, _buddy));
    context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    final sounds = ref.read(soundsProvider);
    Widget picker<T>(String title, List<T> values, T selected, Widget Function(T) face, void Function(T) pick, String key) => Padding(
          padding: const EdgeInsets.only(top: 14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Paper.inkSoft)),
            const SizedBox(height: 8),
            Wrap(spacing: 10, runSpacing: 10, children: [
              for (final v in values)
                Semantics(
                  key: ValueKey('$key-${v is Enum ? v.name : v}'),
                  container: true,
                  button: true,
                  selected: v == selected,
                  label: '$title ${v is Enum ? v.name : v}',
                  excludeSemantics: true,
                  child: Pressable(
                    onTap: () {
                      pick(v);
                      if (v is Buddy) sounds.play(v.sound);
                    },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      width: 68,
                      height: 68,
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: v == selected ? Paper.coral : Paper.edge, width: v == selected ? 4 : 2),
                        boxShadow: const [BoxShadow(color: Color(0x226B4F33), offset: Offset(0, 4), blurRadius: 8)],
                      ),
                      child: face(v),
                    ),
                  ),
                ),
            ]),
          ]),
        );

    const shirtColors = [Color(0xFFF08A8A), Color(0xFFFFD66B), Color(0xFF8FD48F), Color(0xFF7FB8F0), Color(0xFFB79CF0), Color(0xFFF7A8C8)];
    const skinColors = [Color(0xFFFFE3CC), Color(0xFFF2C9A4), Color(0xFFD9A478), Color(0xFFA8714B)];

    return Scaffold(
      body: Sky(
        top: Paper.cream,
        bottom: Paper.page,
        child: SafeArea(
          child: LayoutBuilder(builder: (context, box) {
            final wide = box.maxWidth > 700;
            final puppet = Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: SizedBox(
                height: wide ? 420 : 250,
                child: Stack(alignment: Alignment.bottomCenter, children: [
                  Positioned(bottom: 0, child: SizedBox(height: wide ? 400 : 240, child: Puppet(avatar: _avatar, mood: Mood.happy))),
                  Positioned(bottom: 0, right: wide ? 40 : 10, child: SizedBox(width: wide ? 160 : 100, height: wide ? 160 : 100, child: Bob(child: Art(ArtPath.buddy(_buddy, 'happy'))))),
                ]),
              ),
            );
            final form = ListView(padding: const EdgeInsets.fromLTRB(20, 12, 20, 24), children: [
              const Text(Strings.setupTitle, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700)),
              const SizedBox(height: 10),
              TextField(
                key: const ValueKey('name'),
                controller: _name,
                maxLength: Profile.maxName,
                style: const TextStyle(fontSize: 22),
                decoration: InputDecoration(
                  hintText: Strings.nameHint,
                  hintStyle: const TextStyle(fontSize: 15, color: Paper.inkSoft),
                  filled: true,
                  fillColor: Colors.white,
                  counterText: '',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(18), borderSide: BorderSide.none),
                ),
              ),
              if (!wide) puppet,
              const SizedBox(height: 6),
              const Text(Strings.pickLook, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
              picker(Strings.hair, [1, 2, 3, 4], _avatar.hair, (n) => Art(ArtPath.avatarHair(n)), (n) => setState(() => _avatar = _avatar.copyWith(hair: n)), 'hair'),
              picker(Strings.skin, [1, 2, 3, 4], _avatar.skin, (n) => DecoratedBox(decoration: BoxDecoration(color: skinColors[n - 1], shape: BoxShape.circle)), (n) => setState(() => _avatar = _avatar.copyWith(skin: n)), 'skin'),
              picker(Strings.shirt, [1, 2, 3, 4, 5, 6], _avatar.shirt, (n) => DecoratedBox(decoration: BoxDecoration(color: shirtColors[n - 1], borderRadius: BorderRadius.circular(12))), (n) => setState(() => _avatar = _avatar.copyWith(shirt: n)), 'shirt'),
              picker(Strings.pickBuddy, Buddy.values, _buddy, (b) => Art(ArtPath.buddy(b, 'stand')), (b) => setState(() => _buddy = b), 'buddy'),
              const SizedBox(height: 22),
              Center(child: WideButton(key: const ValueKey('start'), label: Strings.start, icon: Icons.wb_sunny_rounded, color: Paper.coral, onTap: _start, height: 68)),
            ]);
            if (!wide) return form;
            return Row(children: [Expanded(child: Center(child: puppet)), Expanded(child: form)]);
          }),
        ),
      ),
    );
  }
}
