import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/content.dart';
import '../core/game.dart';
import '../core/providers.dart';
import '../features/night/night_screen.dart';
import '../features/parent/parent_gate.dart';
import '../features/parent/parent_screen.dart';
import '../features/play/play_screen.dart';
import '../features/rest/rest_screen.dart';
import '../features/room/room_screen.dart';
import '../features/setup/setup_screen.dart';
import '../features/stickers/sticker_screen.dart';
import 'strings.dart';
import 'theme.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final g = ref.read(gameProvider);
  final resting = g.resting(ref.read(clockProvider)());
  final router = GoRouter(
    initialLocation: resting ? '/rest' : (g.profile == null ? '/setup' : '/'),
    // Always start here, whatever page another app asks the phone to open.
    overridePlatformDefaultLocation: true,
    redirect: (_, state) {
      final at = state.matchedLocation;
      if (at == '/parent' && !ParentPass.take()) return '/';
      if (at != '/setup' && ref.read(gameProvider).profile == null) return '/setup';
      final task = state.pathParameters['task'];
      if (task != null && Task.values.asNameMap()[task] == null) return '/';
      final h = state.pathParameters['happening'];
      if (h != null && Happening.values.asNameMap()[h] == null) return '/';
      return null;
    },
    routes: [
      GoRoute(path: '/', builder: (_, _) => const RoomScreen()),
      GoRoute(path: '/setup', builder: (_, _) => const SetupScreen()),
      GoRoute(path: '/play/task/:task', builder: (_, s) => PlayScreen(key: ValueKey(s.matchedLocation), task: Task.values.byName(s.pathParameters['task']!))),
      GoRoute(path: '/play/happening/:happening', builder: (_, s) => PlayScreen(key: ValueKey(s.matchedLocation), happening: Happening.values.byName(s.pathParameters['happening']!))),
      GoRoute(path: '/stickers', builder: (_, _) => const StickerScreen()),
      GoRoute(path: '/night', builder: (_, _) => const NightScreen()),
      GoRoute(path: '/rest', builder: (_, _) => const RestScreen()),
      GoRoute(path: '/parent', builder: (_, _) => const ParentScreen()),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});

class LittleLifeApp extends ConsumerWidget {
  const LittleLifeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(gameProvider.select((g) => g.settings));
    ref.read(soundsProvider)
      ..music = settings.music
      ..effects = settings.sounds;
    return MaterialApp.router(
      title: Strings.appName,
      debugShowCheckedModeBanner: false,
      theme: PaperTheme.light(),
      locale: const Locale('zh', 'TW'),
      supportedLocales: const [Locale('zh', 'TW')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      routerConfig: ref.watch(routerProvider),
      builder: (_, child) => RestGuard(child: child ?? const SizedBox()),
    );
  }
}

/// Keeps the parent's play time (docs/design.md 「每次玩多久」): when the
/// sitting has gone on for the minutes they set, the character goes to
/// sleep and the house goes dark; an hour later (or when a parent says so)
/// play can go on. A little game being played is finished first (at most
/// [finishGame] more). Time at the parent gate and in parent mode is not
/// the child's play time, and neither is time with the app out of sight:
/// nothing is checked then and no rest starts. Away (or closed) for ten
/// minutes counts as a rest; closed for less, the sitting goes on where it
/// was ([Sitting], saved every [saveEvery] seconds and when the app goes
/// out of sight). A phone clock moved back gives no extra time and does
/// not end a rest early.
class RestGuard extends ConsumerStatefulWidget {
  const RestGuard({super.key, required this.child});

  final Widget child;

  static const check = Duration(seconds: 2);
  static const awayIsRest = Sitting.keep;

  /// How long a little game being played may go on after the time is up.
  static const finishGame = Duration(minutes: 2);

  /// The sitting is saved this often (seconds).
  static const saveEvery = 30;

  @override
  ConsumerState<RestGuard> createState() => _RestGuardState();
}

class _RestGuardState extends ConsumerState<RestGuard> {
  Timer? _timer;
  AppLifecycleListener? _life;
  late final GoRouter _router;
  DateTime? _away;

  /// When a parent page (the gate, parent mode) was opened, and the time
  /// spent on them not given back to the child yet. Looked at the moment a
  /// page opens or closes, not only on the next check.
  DateTime? _parentSince;
  var _parentFor = Duration.zero;

  /// The phone's clock at the last check (to see it moved back).
  DateTime? _last;
  var _unsaved = 0;

  /// The clock (kept, so a page closing while the app itself closes can
  /// still be looked at).
  late final DateTime Function() _clock;

  DateTime get _now => _clock();

  String get _path => _router.routerDelegate.currentConfiguration.isEmpty ? '' : _router.state.matchedLocation;

  @override
  void initState() {
    super.initState();
    ref.read(sessionStartProvider);
    _clock = ref.read(clockProvider);
    _router = ref.read(routerProvider);
    _router.routerDelegate.addListener(_lookParent);
    ParentGatePage.showing.addListener(_lookParent);
    _timer = Timer.periodic(RestGuard.check, (_) => _check());
    _life = AppLifecycleListener(
      onHide: () {
        final now = _now;
        _away = now;
        _lookParent();
        _giveBackParent();
        _save(now);
      },
      onShow: () {
        final away = _away;
        _away = null;
        if (away != null) _back(away);
        _lookParent();
        _check();
      },
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _life?.dispose();
    _router.routerDelegate.removeListener(_lookParent);
    ParentGatePage.showing.removeListener(_lookParent);
    super.dispose();
  }

  /// A page opened or closed (or the app went out of sight): time on a
  /// parent page starts or stops counting as the parent's.
  void _lookParent() {
    if (!mounted) return;
    final now = _now;
    if (_away == null && _parentOpen(_path)) {
      _parentSince ??= now;
      return;
    }
    final since = _parentSince;
    if (since == null) return;
    _parentSince = null;
    final d = now.difference(since);
    if (!d.isNegative) _parentFor += d;
  }

  /// Back from the background, gone since [away]: ten minutes or more is a
  /// rest (a new sitting); less is not the child's play time either, so the
  /// sitting goes on where it was (a clock moved back meanwhile makes the
  /// time gone negative and takes that back too).
  void _back(DateTime away) {
    final now = _now;
    final gone = now.difference(away);
    _last = now;
    if (gone >= RestGuard.awayIsRest) {
      ref.read(sessionStartProvider.notifier).restart();
      if (_parentSince != null) _parentSince = now;
      return;
    }
    _moveSitting(gone);
    final since = ref.read(gameProvider).restSince;
    if (gone.isNegative && since != null) ref.read(gameProvider.notifier).change((g) => g.copyWith(restSince: since.add(gone)));
  }

  /// Moves the sitting (and a parent page's start, so its time is not given
  /// back twice) by [d].
  void _moveSitting(Duration d) {
    ref.read(sessionStartProvider.notifier).shift(d);
    final p = _parentSince;
    if (p != null) _parentSince = p.add(d);
  }

  /// The time on parent pages is not played: the sitting starts that much
  /// later.
  void _giveBackParent() {
    if (_parentFor <= Duration.zero) return;
    ref.read(sessionStartProvider.notifier).shift(_parentFor);
    _parentFor = Duration.zero;
  }

  /// Keeps the sitting, so an app closed and opened again soon goes on.
  void _save(DateTime now) {
    _unsaved = 0;
    final g = ref.read(gameProvider);
    if (g.restSince != null) return;
    final used = ref.read(sessionStartProvider.notifier).usedAt(now);
    ref.read(gameProvider.notifier).change((g) => g.copyWith(sitting: Sitting(used.inSeconds, now)));
  }

  bool _parentOpen(String path) => path.startsWith('/parent') || ParentGatePage.showing.value > 0;

  void _check() {
    // Nothing while the app is out of sight (its timer can go on in the
    // background): that time is not played, and it is given back on return.
    if (!mounted || _away != null) return;
    final now = _now;
    final game = ref.read(gameProvider.notifier);
    // The phone's clock moved back: the sitting moves back with it, and so
    // does a rest (it neither ends early nor lasts longer).
    final last = _last;
    _last = now;
    if (last != null && now.isBefore(last)) {
      final back = now.difference(last);
      _moveSitting(back);
      final since = ref.read(gameProvider).restSince;
      if (since != null) game.change((g) => g.copyWith(restSince: since.add(back)));
    }
    // A rest that seems to start later than now (the clock was moved back
    // while the app was closed) starts now: at most an hour more.
    final since = ref.read(gameProvider).restSince;
    if (since != null && now.isBefore(since)) game.change((g) => g.copyWith(restSince: now));
    final g = ref.read(gameProvider);
    final router = _router;
    final path = _path;
    _lookParent();
    _giveBackParent();
    if (_parentOpen(path) || path.isEmpty || path == '/setup') return;
    if (g.restSince != null) {
      if (g.resting(now)) {
        if (path != '/rest') router.go('/rest');
        return;
      }
      game.change((g) => g.playOn());
      ref.read(sessionStartProvider.notifier).restart();
      _save(now);
      if (path == '/rest') router.go('/');
      return;
    }
    if (path == '/rest') return;
    _unsaved += RestGuard.check.inSeconds;
    if (_unsaved >= RestGuard.saveEvery) _save(now);
    final over = ref.read(sessionStartProvider.notifier).usedAt(now) - Duration(minutes: g.settings.minutes);
    if (!over.isNegative) {
      // A little game being played is finished first (at most two minutes).
      if (ref.read(busyProvider).busy && over < RestGuard.finishGame) return;
      game.change((g) => g.rest(now));
      router.go('/rest');
    }
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
