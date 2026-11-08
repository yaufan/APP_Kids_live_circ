import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:little_life/core/game.dart';
import 'package:little_life/features/parent/parent_gate.dart';

import 'helpers.dart';

/// Privacy and the parent gate (docs/design.md: no network, nothing leaves
/// the phone, parent mode only through the gate).
void main() {
  test('the app asks for no permissions and takes no links from other apps', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, isNot(contains('uses-permission')), reason: 'no internet, camera, location…');
    expect(manifest, contains('android:name="flutter_deeplinking_enabled" android:value="false"'));
    expect(File('ios/Runner/Info.plist').readAsStringSync(), contains('<key>FlutterDeepLinkingEnabled</key>\n\t<false/>'));
    expect(File('pubspec.yaml').readAsStringSync(), isNot(contains('source: system')));
  });

  testWidgets('parent mode and unknown pages cannot be opened without the gate', (tester) async {
    final app = await TestApp.start(tester, game: const Game(profile: Profile(name: '小明')));
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'no pass from the gate');
    ParentPass.grant();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/parent', reason: 'right after the gate');
    app.go('/');
    await app.settle();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'the pass is used up');
    for (final bad in ['/play/task/nothing', '/play/happening/nothing']) {
      app.go(bad);
      await app.settle();
      expect(app.location, '/', reason: bad);
    }
    await app.end();
  });

  testWidgets('without a child the app starts at the setup page and goes nowhere else', (tester) async {
    final app = await TestApp.start(tester);
    expect(app.location, '/setup');
    app.go('/stickers');
    await app.settle();
    expect(app.location, '/setup');
    await app.end();
  });
}
