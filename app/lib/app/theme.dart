import 'package:flutter/material.dart';

/// The app's colours (docs/design.md 「畫風」: soft paper — pink, mint, cream
/// yellow; dark brown words).
abstract final class Paper {
  static const ink = Color(0xFF4A3B32);
  static const inkSoft = Color(0xFF9A8578);
  static const cream = Color(0xFFFFF7E8);
  static const page = Color(0xFFFBEFD9);
  static const pink = Color(0xFFF7A8B8);
  static const mint = Color(0xFF9EDCC8);
  static const yellow = Color(0xFFFFE08A);
  static const sky = Color(0xFFA9D8F5);
  static const lavender = Color(0xFFC9B8F0);
  static const peach = Color(0xFFFFC7A0);
  static const green = Color(0xFF6CC070);
  static const coral = Color(0xFFEF7B6B);
  static const gold = Color(0xFFFFC53D);
  static const glow = Color(0xFFFFE45C);
  static const wood = Color(0xFFC89B6A);
  static const card = Colors.white;
  static const edge = Color(0xFFE9D9C2);
  static const night = Color(0xFF1F2450);
  static const parentBg = Color(0xFFF5F2EE);
}

abstract final class PaperTheme {
  /// jf open 粉圓 (OFL): a rounded typeface made in Taiwan.
  static const font = 'Huninn';

  static ThemeData light() {
    final base = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Paper.pink, surface: Paper.cream),
      scaffoldBackgroundColor: Paper.cream,
      fontFamily: font,
      materialTapTargetSize: MaterialTapTargetSize.padded,
    );
    return base.copyWith(textTheme: base.textTheme.apply(bodyColor: Paper.ink, displayColor: Paper.ink, fontFamily: font));
  }
}

/// The sky through the windows for a weather and a part of the day
/// (bg.svg's `#SKY` is painted with it).
Color skyColor(String weather, {bool night = false, bool evening = false}) {
  if (night) return const Color(0xFF2B3470);
  if (evening) return const Color(0xFFF7B37A);
  return switch (weather) {
    'rain' => const Color(0xFF9FB3C8),
    'storm' => const Color(0xFF6F7E99),
    'cold' => const Color(0xFFCFE3F2),
    'hot' => const Color(0xFF86CBF5),
    _ => const Color(0xFFA9D8F5),
  };
}
