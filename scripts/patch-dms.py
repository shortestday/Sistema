"""Small, version-checked UI fixes applied to a writable copy of pinned DMS."""
import json
from pathlib import Path
import sys


def replace_once(root, relative, before, after):
    path = root / relative
    content = path.read_text()
    if content.count(before) != 1:
        raise RuntimeError(f"DMS changed; review UI patch: {relative}")
    path.write_text(content.replace(before, after), encoding="utf-8")


def patch(root, translations):
    replace_once(root, "Widgets/DankScrollbar.qml",
                 "opacity: (policy !== ScrollBar.AlwaysOff && _shouldShow) ? 1.0 : 0.0",
                 "opacity: policy !== ScrollBar.AlwaysOff ? 1.0 : 0.0")
    replace_once(root, "Widgets/DankScrollbar.qml",
                 "implicitWidth: 10", "implicitWidth: 14")
    replace_once(root, "Widgets/DankScrollbar.qml",
                 "implicitWidth: 6", "implicitWidth: 8")
    replace_once(root, "Widgets/DankScrollbar.qml",
                 "opacity: scrollbar.pressed ? 1.0 : scrollbar._shouldShow ? 1.0 : 0.6",
                 "opacity: 1.0")
    replace_once(root, "Modules/Settings/KeybindsTab.qml",
                 "return cat;", "return I18n.tr(cat);")
    replace_once(root, "Widgets/KeybindItem.qml",
                 'text: root.bindData.category || ""',
                 'text: I18n.tr(root.bindData.category || "")')
    path = root / "translations/poexports/es.json"
    catalog = json.loads(path.read_text())
    additions = json.loads(translations.read_text())
    for term, translated in additions.items():
        assert translated and isinstance(translated, str)
        # Keep existing contexts: I18n.tr searches all contexts for missing strings.
        for context in catalog.values():
            if term in context:
                context[term] = translated
        catalog.setdefault(term, {})[term] = translated
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    patch(Path(sys.argv[1]), Path(sys.argv[2]))
