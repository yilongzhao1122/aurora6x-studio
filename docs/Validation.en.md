# v3.3.2 validation

Fonts and the offline settings preview were regenerated. A0, A2, B0, A4 and C6 use SmallPlus at nominal size 16. C1 uses Ring0–Ring5 with 22px digit ink height and unchanged character advances. B3, C0 and the four lower slots retain their existing font references.

Local checks use source-drawing doubles and the actual FNT/PNG bitmaps. The 636 typeface/hour-format/metric scenes check text overlap, screen bounds and the light background beneath the central clock. Separate scripts check menu saving, settings export, metric behavior and the position guide.

These checks do not execute the Garmin VM. SDK compilation, official device-package simulator execution and physical watch testing have not been performed for v3.3.2 in this environment. Compilation results from earlier versions are not evidence for this version.

This is a source release with generated resources, not a precompiled PRG release. Build using the official fenix6xpro device package and your own key. Check real peak RAM, battery use, long Chinese text, extreme values and live sensor behavior on the target. All preview images use sample data.
