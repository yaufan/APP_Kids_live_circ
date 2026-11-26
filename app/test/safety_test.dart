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

  test('the phone\'s speech engine can be found on Android 11 and later', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, contains('<action android:name="android.intent.action.TTS_SERVICE" />'));
    expect(RegExp(r'<queries>[\s\S]*TTS_SERVICE[\s\S]*</queries>').hasMatch(manifest), isTrue);
  });

  test('nothing is backed up to the cloud or moved to another phone: it stays on this one', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, contains('android:allowBackup="false"'));
    expect(manifest, contains('android:fullBackupContent="false"'));
    expect(manifest, contains('android:dataExtractionRules="@xml/data_extraction_rules"'));
    final rules = File('android/app/src/main/res/xml/data_extraction_rules.xml').readAsStringSync();
    for (final part in ['cloud-backup', 'device-transfer']) {
      final block = RegExp('<$part>([\\s\\S]*?)</$part>').firstMatch(rules)!.group(1)!;
      for (final domain in ['root', 'file', 'database', 'sharedpref', 'external']) {
        expect(block, contains('<exclude domain="$domain" />'), reason: '$part $domain');
      }
    }
  });

  test('the build checks the packages ask for no network, location, camera, microphone, contacts or photos', () {
    for (final w in ['../.github/workflows/app.yml', '../.github/workflows/release.yml']) {
      final text = File(w).readAsStringSync();
      for (final p in ['INTERNET', 'LOCATION', 'AD_ID', 'CAMERA', 'RECORD_AUDIO', 'READ_CONTACTS', 'READ_MEDIA_', 'READ_EXTERNAL_STORAGE']) {
        expect(text, contains(p), reason: '$w $p');
      }
    }
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
