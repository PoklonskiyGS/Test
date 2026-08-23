"use client";

import type { Session, RolledMod } from "./CraftingApp";
import { ITEM_BASES, POE_MODS } from "@/lib/poe-data";

type Props = {
  session: Session;
};

function getRarityColor(rarity: string) {
  if (rarity === "rare") return "#ffff77";
  if (rarity === "magic") return "#8888ff";
  return "#c8c8c8";
}

function getRarityName(rarity: string) {
  if (rarity === "rare") return "Редкий";
  if (rarity === "magic") return "Магический";
  return "Обычный";
}

function getBorderColor(rarity: string) {
  if (rarity === "rare") return "#c8a951";
  if (rarity === "magic") return "#5555cc";
  return "#666";
}

export default function ItemDisplay({ session }: Props) {
  const itemBase = ITEM_BASES.find((b) => b.id === session.itemBase) || ITEM_BASES[0];
  const mods: RolledMod[] = session.currentMods || [];
  const prefixes = mods.filter((m) => m.type === "prefix");
  const suffixes = mods.filter((m) => m.type === "suffix");

  const targetModIds = new Set([
    ...(session.targetPrefixes || []),
    ...(session.targetSuffixes || []),
  ]);

  const isModMatched = (mod: RolledMod) => targetModIds.has(mod.modId);

  const formatModText = (mod: RolledMod) => {
    return mod.description.replace("#", String(mod.rolledValue));
  };

  const rarityColor = getRarityColor(session.rarity);
  const borderColor = getBorderColor(session.rarity);

  return (
    <div className="p-4">
      {/* Item card */}
      <div
        className="relative mx-auto"
        style={{
          maxWidth: 340,
          border: `1px solid ${borderColor}`,
          background: "linear-gradient(180deg, #1a1405 0%, #0d0a02 100%)",
        }}
      >
        {/* Top border deco */}
        <div style={{ height: 3, background: `linear-gradient(90deg, transparent, ${borderColor}, transparent)` }} />

        {/* Item Name Header */}
        <div className="px-4 py-3 text-center" style={{ background: "rgba(0,0,0,0.3)" }}>
          <div className="font-bold text-base" style={{ color: rarityColor, textShadow: `0 0 8px ${rarityColor}40` }}>
            {session.rarity === "normal" ? itemBase.name : (
              <>
                {mods.length > 0 ? (
                  <span>{mods[0]?.tierName || ""} {itemBase.name}</span>
                ) : itemBase.name}
              </>
            )}
          </div>
          <div className="text-xs mt-1" style={{ color: "#888" }}>
            {itemBase.name} · {getRarityName(session.rarity)} · iLvl {session.itemLevel}
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: `linear-gradient(90deg, transparent, ${borderColor}88, transparent)` }} />

        {/* Item type */}
        <div className="px-4 py-1 text-center text-xs" style={{ color: "#888" }}>
          {itemBase.subType.charAt(0).toUpperCase() + itemBase.subType.slice(1)}
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: `linear-gradient(90deg, transparent, ${borderColor}44, transparent)` }} />

        {/* Implicits */}
        {itemBase.implicits && itemBase.implicits.length > 0 && (
          <>
            <div className="px-4 py-2">
              {itemBase.implicits.map((impl, i) => (
                <div key={i} className="text-center text-sm" style={{ color: "#c8c8c8" }}>
                  {impl}
                </div>
              ))}
            </div>
            <div style={{ height: 1, background: `linear-gradient(90deg, transparent, ${borderColor}44, transparent)` }} />
          </>
        )}

        {/* Mods */}
        <div className="px-4 py-3">
          {mods.length === 0 ? (
            <div className="text-center text-sm py-4" style={{ color: "#444" }}>
              <div className="text-2xl mb-2 opacity-30">⬡</div>
              <div>Нет модификаторов</div>
              <div className="text-xs mt-1" style={{ color: "#333" }}>Примените валюту для крафта</div>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {prefixes.length > 0 && (
                <>
                  <div className="text-xs mb-1" style={{ color: "#555" }}>— Префиксы —</div>
                  {prefixes.map((mod, i) => (
                    <ModLine key={i} mod={mod} isMatched={isModMatched(mod)} formatText={formatModText} />
                  ))}
                </>
              )}
              {suffixes.length > 0 && (
                <>
                  <div className="text-xs mt-2 mb-1" style={{ color: "#555" }}>— Суффиксы —</div>
                  {suffixes.map((mod, i) => (
                    <ModLine key={i} mod={mod} isMatched={isModMatched(mod)} formatText={formatModText} />
                  ))}
                </>
              )}
            </div>
          )}
        </div>

        {/* Bottom border deco */}
        <div style={{ height: 3, background: `linear-gradient(90deg, transparent, ${borderColor}, transparent)` }} />
      </div>

      {/* Stats summary */}
      <div className="mt-4 grid grid-cols-2 gap-2 text-xs" style={{ color: "#666" }}>
        <div className="poe-panel rounded px-3 py-2">
          <div className="font-bold mb-1" style={{ color: "#888" }}>Префиксы</div>
          <div style={{ color: "#8888ff" }}>{prefixes.length} / 3</div>
        </div>
        <div className="poe-panel rounded px-3 py-2">
          <div className="font-bold mb-1" style={{ color: "#888" }}>Суффиксы</div>
          <div style={{ color: "#88cc88" }}>{suffixes.length} / 3</div>
        </div>
      </div>
    </div>
  );
}

function ModLine({
  mod,
  isMatched,
  formatText,
}: {
  mod: RolledMod;
  isMatched: boolean;
  formatText: (mod: RolledMod) => string;
}) {
  const baseColor = mod.type === "prefix" ? "#88aaff" : "#aaffaa";
  const color = isMatched ? "#ffff44" : baseColor;

  return (
    <div
      className="text-sm leading-snug flex items-start gap-1"
      style={{
        color,
        textShadow: isMatched ? "0 0 6px rgba(255,255,68,0.4)" : undefined,
      }}
    >
      {isMatched && <span className="text-xs mt-0.5">★</span>}
      <span>{formatText(mod)}</span>
      <span className="ml-auto text-xs opacity-40 flex-shrink-0">T{mod.tier}</span>
    </div>
  );
}
