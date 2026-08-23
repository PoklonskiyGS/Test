"use client";

import { useState, useMemo } from "react";
import { POE_MODS, getModsForItemType, getAvailableTier } from "@/lib/poe-data";
import type { ItemBase, PoEMod } from "@/lib/poe-data";
import type { RolledMod } from "./CraftingApp";

type Props = {
  itemBase: ItemBase;
  itemLevel: number;
  targetPrefixes: string[];
  targetSuffixes: string[];
  currentMods: RolledMod[];
  onUpdate: (prefixes: string[], suffixes: string[]) => void;
};

const CATEGORY_COLORS: Record<string, string> = {
  Life: "#cc4444",
  Defence: "#4488cc",
  Damage: "#cc8844",
  Mana: "#4488ff",
  Resistance: "#44cc88",
  Attribute: "#cc88cc",
  Critical: "#ffff44",
  Attack: "#ff8844",
  Caster: "#aa66ff",
  Movement: "#44cccc",
  Utility: "#888888",
};

export default function ModSelector({
  itemBase,
  itemLevel,
  targetPrefixes,
  targetSuffixes,
  currentMods,
  onUpdate,
}: Props) {
  const [tab, setTab] = useState<"prefix" | "suffix">("prefix");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  const availableMods = useMemo(() => getModsForItemType(itemBase, itemLevel), [itemBase, itemLevel]);

  const filteredMods = useMemo(() => {
    return availableMods.filter((mod) => {
      if (mod.type !== tab) return false;
      if (categoryFilter !== "all" && mod.category !== categoryFilter) return false;
      if (search) {
        const q = search.toLowerCase();
        return (
          mod.name.toLowerCase().includes(q) ||
          mod.description.toLowerCase().includes(q) ||
          mod.category.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [availableMods, tab, search, categoryFilter]);

  const categories = useMemo(() => {
    const cats = new Set(availableMods.filter((m) => m.type === tab).map((m) => m.category));
    return ["all", ...Array.from(cats)];
  }, [availableMods, tab]);

  const currentModIds = useMemo(() => new Set(currentMods.map((m) => m.modId)), [currentMods]);

  const toggleMod = (mod: PoEMod) => {
    const isPrefix = mod.type === "prefix";
    const currentList = isPrefix ? [...targetPrefixes] : [...targetSuffixes];
    const idx = currentList.indexOf(mod.id);

    let newList: string[];
    if (idx >= 0) {
      newList = currentList.filter((id) => id !== mod.id);
    } else {
      if (isPrefix && targetPrefixes.length >= 3) return;
      if (!isPrefix && targetSuffixes.length >= 3) return;
      newList = [...currentList, mod.id];
    }

    if (isPrefix) {
      onUpdate(newList, targetSuffixes);
    } else {
      onUpdate(targetPrefixes, newList);
    }
  };

  const isSelected = (mod: PoEMod) => {
    if (mod.type === "prefix") return targetPrefixes.includes(mod.id);
    return targetSuffixes.includes(mod.id);
  };

  const isOnItem = (mod: PoEMod) => currentModIds.has(mod.id);

  const targetCount = tab === "prefix" ? targetPrefixes.length : targetSuffixes.length;
  const currentTabMods = tab === "prefix" ? targetPrefixes : targetSuffixes;

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex" style={{ borderBottom: "1px solid #3d2e0a" }}>
        {(["prefix", "suffix"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className="flex-1 py-2 text-xs font-bold transition-colors"
            style={{
              color: tab === t ? (t === "prefix" ? "#88aaff" : "#aaffaa") : "#555",
              background: tab === t ? "rgba(255,255,255,0.04)" : "transparent",
              borderBottom: tab === t ? `2px solid ${t === "prefix" ? "#88aaff" : "#aaffaa"}` : "2px solid transparent",
            }}
          >
            {t === "prefix" ? "Префиксы" : "Суффиксы"}
            <span className="ml-1 text-xs" style={{ color: "#666" }}>
              ({tab === t ? targetCount : tab === "prefix" ? targetSuffixes.length : targetPrefixes.length}/3)
            </span>
          </button>
        ))}
      </div>

      {/* Selected target mods summary */}
      {currentTabMods.length > 0 && (
        <div className="px-3 py-2" style={{ borderBottom: "1px solid #1f1505", background: "rgba(0,0,0,0.2)" }}>
          <div className="text-xs mb-1" style={{ color: "#888" }}>Выбрано:</div>
          {currentTabMods.map((modId) => {
            const mod = POE_MODS.find((m) => m.id === modId);
            if (!mod) return null;
            const onItem = currentModIds.has(modId);
            return (
              <div key={modId} className="flex items-center justify-between text-xs py-0.5">
                <span style={{ color: onItem ? "#44cc44" : tab === "prefix" ? "#88aaff" : "#aaffaa" }}>
                  {onItem ? "✅ " : "⬜ "}
                  {mod.name}
                </span>
                <button
                  onClick={() => toggleMod(mod)}
                  className="text-xs opacity-50 hover:opacity-100"
                  style={{ color: "#cc4444" }}
                >
                  ✕
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Search */}
      <div className="px-3 py-2" style={{ borderBottom: "1px solid #1f1505" }}>
        <input
          className="poe-input text-xs"
          placeholder="Поиск модов..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Category filter */}
      <div className="px-3 py-1 flex gap-1 flex-wrap" style={{ borderBottom: "1px solid #1f1505" }}>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className="text-xs px-2 py-0.5 rounded transition-colors"
            style={{
              background: categoryFilter === cat ? "rgba(200,169,81,0.2)" : "rgba(255,255,255,0.03)",
              border: `1px solid ${categoryFilter === cat ? "#c8a951" : "#2a1f08"}`,
              color: categoryFilter === cat ? "#c8a951" : cat === "all" ? "#888" : (CATEGORY_COLORS[cat] || "#888"),
              fontSize: "0.65rem",
            }}
          >
            {cat === "all" ? "Все" : cat}
          </button>
        ))}
      </div>

      {/* Mod List */}
      <div className="flex-1 overflow-y-auto" style={{ maxHeight: 360 }}>
        {filteredMods.length === 0 ? (
          <div className="p-4 text-center text-xs" style={{ color: "#444" }}>
            Нет доступных модов для этого предмета
          </div>
        ) : (
          filteredMods.map((mod) => {
            const selected = isSelected(mod);
            const onItem = isOnItem(mod);
            const tier = getAvailableTier(mod, itemLevel);
            const catColor = CATEGORY_COLORS[mod.category] || "#888";
            const canSelect = tab === "prefix"
              ? targetPrefixes.length < 3 || selected
              : targetSuffixes.length < 3 || selected;

            return (
              <div
                key={mod.id}
                onClick={() => canSelect && toggleMod(mod)}
                className="px-3 py-2 transition-colors flex items-start gap-2"
                style={{
                  borderBottom: "1px solid #0f0a00",
                  background: selected
                    ? "rgba(200,169,81,0.06)"
                    : onItem
                    ? "rgba(68,204,68,0.04)"
                    : "transparent",
                  cursor: canSelect ? "pointer" : "not-allowed",
                  opacity: canSelect ? 1 : 0.5,
                }}
              >
                <input
                  type="checkbox"
                  className="poe-checkbox mt-0.5 flex-shrink-0"
                  checked={selected}
                  readOnly
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold" style={{ color: tab === "prefix" ? "#88aaff" : "#aaffaa" }}>
                      {mod.name}
                    </span>
                    <span
                      className="text-xs px-1"
                      style={{
                        background: `${catColor}18`,
                        border: `1px solid ${catColor}44`,
                        color: catColor,
                        fontSize: "0.65rem",
                      }}
                    >
                      {mod.category}
                    </span>
                    {onItem && (
                      <span className="text-xs" style={{ color: "#44cc44" }}>✅ На предмете</span>
                    )}
                  </div>
                  <div className="text-xs mt-0.5" style={{ color: "#888" }}>{mod.description}</div>
                  {tier && (
                    <div className="text-xs mt-0.5" style={{ color: "#666" }}>
                      T{tier.tier} · {tier.values} · iLvl {tier.minIlvl}+
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
