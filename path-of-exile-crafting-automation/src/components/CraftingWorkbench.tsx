"use client";

import { useState, useCallback } from "react";
import type { Session, RolledMod } from "./CraftingApp";
import { CURRENCIES, ITEM_BASES, POE_MODS } from "@/lib/poe-data";
import { getCraftingRecommendation } from "@/lib/crafting-engine";
import ItemDisplay from "./ItemDisplay";
import ModSelector from "./ModSelector";
import CurrencyInventory from "./CurrencyInventory";

type Props = {
  session: Session;
  onUpdate: (session: Session) => void;
};

export default function CraftingWorkbench({ session, onUpdate }: Props) {
  const [loading, setLoading] = useState(false);
  const [lastMessage, setLastMessage] = useState<string>("");
  const [selectedCurrency, setSelectedCurrency] = useState<string | null>(null);
  const [autoCraft, setAutoCraft] = useState(false);
  const [attemptsThisRun, setAttemptsThisRun] = useState<number | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const itemBase = ITEM_BASES.find((b) => b.id === session.itemBase) || ITEM_BASES[0];

  const handleCraft = useCallback(async () => {
    if (!selectedCurrency) return;
    setLoading(true);
    setIsSuccess(false);

    try {
      const res = await fetch("/api/craft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: session.id,
          currencyId: selectedCurrency,
          autoCraft,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setLastMessage(data.message);
        setAttemptsThisRun(data.attemptsThisRun);
        setIsSuccess(data.isComplete);
        onUpdate(data.session);
      } else {
        const err = await res.json();
        setLastMessage("❌ " + (err.error || "Ошибка крафта"));
      }
    } catch {
      setLastMessage("❌ Ошибка соединения");
    } finally {
      setLoading(false);
    }
  }, [selectedCurrency, session.id, autoCraft, onUpdate]);

  const handleReset = useCallback(async () => {
    if (!confirm("Сбросить предмет к Normal?")) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/sessions/${session.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rarity: "normal",
          currentMods: [],
          attempts: 0,
          currencyUsed: {},
          isComplete: false,
        }),
      });
      if (res.ok) {
        const updated = await res.json();
        setLastMessage("🧹 Предмет сброшен");
        setAttemptsThisRun(null);
        setIsSuccess(false);
        onUpdate(updated);
      }
    } finally {
      setLoading(false);
    }
  }, [session.id, onUpdate]);

  const handleTargetUpdate = useCallback(
    async (targetPrefixes: string[], targetSuffixes: string[]) => {
      const res = await fetch(`/api/sessions/${session.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ targetPrefixes, targetSuffixes }),
      });
      if (res.ok) {
        const updated = await res.json();
        onUpdate(updated);
      }
    },
    [session.id, onUpdate]
  );

  const recommendation = getCraftingRecommendation(
    {
      base: session.itemBase,
      itemLevel: session.itemLevel,
      rarity: session.rarity as "normal" | "magic" | "rare",
      mods: session.currentMods || [],
    },
    session.targetPrefixes || [],
    session.targetSuffixes || []
  );

  const currencyInfo = CURRENCIES.find((c) => c.id === selectedCurrency);
  const prefixCount = (session.currentMods || []).filter((m) => m.type === "prefix").length;
  const suffixCount = (session.currentMods || []).filter((m) => m.type === "suffix").length;

  const isCurrencyValid = useCallback(
    (currId: string) => {
      const rarity = session.rarity;
      switch (currId) {
        case "orb_of_transmutation":
        case "orb_of_alchemy":
          return rarity === "normal";
        case "orb_of_alteration":
        case "orb_of_augmentation":
        case "regal_orb":
          return rarity === "magic";
        case "orb_of_chaos":
        case "exalted_orb":
          return rarity === "rare";
        case "orb_of_scouring":
          return rarity !== "normal";
        case "annulment_orb":
          return (session.currentMods || []).length > 0;
        case "divine_orb":
          return (session.currentMods || []).length > 0;
        default:
          return true;
      }
    },
    [session.rarity, session.currentMods]
  );

  return (
    <div className="flex flex-col gap-4">
      {/* Top bar */}
      <div className="poe-panel rounded px-4 py-3 flex items-center gap-4 flex-wrap">
        <div>
          <span className="text-xs" style={{ color: "#888" }}>Предмет: </span>
          <span className="font-bold" style={{ color: "#c8c8c8" }}>{itemBase.name}</span>
          <span className="text-xs ml-2 poe-tag">{itemBase.subType}</span>
        </div>
        <div>
          <span className="text-xs" style={{ color: "#888" }}>iLvl: </span>
          <span className="font-bold" style={{ color: "#c8a951" }}>{session.itemLevel}</span>
        </div>
        <div>
          <span className="text-xs" style={{ color: "#888" }}>Редкость: </span>
          <span
            className="font-bold capitalize"
            style={{
              color:
                session.rarity === "rare"
                  ? "#ffff77"
                  : session.rarity === "magic"
                  ? "#8888ff"
                  : "#c8c8c8",
            }}
          >
            {session.rarity === "normal" ? "Обычный" : session.rarity === "magic" ? "Магический" : "Редкий"}
          </span>
        </div>
        <div>
          <span className="text-xs" style={{ color: "#888" }}>Попыток: </span>
          <span className="font-bold" style={{ color: "#c8a951" }}>{session.attempts}</span>
        </div>
        <div className="ml-auto flex gap-2">
          <button onClick={handleReset} className="poe-btn poe-btn-danger text-xs px-3 py-1">
            🧹 Сброс
          </button>
        </div>
      </div>

      {/* Main 3-column layout */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Column 1: Target Mods */}
        <div className="poe-panel rounded overflow-hidden">
          <div className="px-4 py-2" style={{ borderBottom: "1px solid #3d2e0a" }}>
            <span className="font-bold text-sm" style={{ color: "#c8a951" }}>🎯 Целевые Моды</span>
          </div>
          <ModSelector
            itemBase={itemBase}
            itemLevel={session.itemLevel}
            targetPrefixes={session.targetPrefixes || []}
            targetSuffixes={session.targetSuffixes || []}
            currentMods={session.currentMods || []}
            onUpdate={handleTargetUpdate}
          />
        </div>

        {/* Column 2: Item Display */}
        <div className="poe-panel rounded overflow-hidden">
          <div className="px-4 py-2 flex items-center justify-between" style={{ borderBottom: "1px solid #3d2e0a" }}>
            <span className="font-bold text-sm" style={{ color: "#c8a951" }}>🗡️ Предмет</span>
            <div className="text-xs" style={{ color: "#888" }}>
              P: {prefixCount}/3 · S: {suffixCount}/3
            </div>
          </div>
          <ItemDisplay session={session} />

          {/* Status message */}
          {lastMessage && (
            <div
              className={`mx-4 mb-3 px-3 py-2 text-xs rounded ${isSuccess ? "flash-success" : ""}`}
              style={{
                background: isSuccess ? "rgba(68,204,68,0.1)" : "rgba(0,0,0,0.4)",
                border: `1px solid ${isSuccess ? "#44cc44" : "#3d2e0a"}`,
                color: isSuccess ? "#44cc44" : "#c8c8c8",
              }}
            >
              {lastMessage}
              {attemptsThisRun !== null && attemptsThisRun > 1 && (
                <span className="ml-2" style={{ color: "#888" }}>({attemptsThisRun} попыток)</span>
              )}
            </div>
          )}

          {session.isComplete && (
            <div className="mx-4 mb-4 px-3 py-3 text-center rounded" style={{ background: "rgba(68,204,68,0.1)", border: "1px solid #44cc44" }}>
              <div className="text-lg mb-1">🏆</div>
              <div className="text-sm font-bold" style={{ color: "#44cc44" }}>Цель достигнута!</div>
              <div className="text-xs mt-1" style={{ color: "#888" }}>Все целевые моды найдены</div>
            </div>
          )}
        </div>

        {/* Column 3: Currency & Crafting */}
        <div className="poe-panel rounded overflow-hidden">
          <div className="px-4 py-2" style={{ borderBottom: "1px solid #3d2e0a" }}>
            <span className="font-bold text-sm" style={{ color: "#c8a951" }}>💰 Крафт Валюта</span>
          </div>

          <div className="p-4 flex flex-col gap-4">
            {/* Currency Grid */}
            <CurrencyInventory
              selectedCurrency={selectedCurrency}
              onSelect={setSelectedCurrency}
              isCurrencyValid={isCurrencyValid}
              currencyUsed={session.currencyUsed || {}}
            />

            {/* Selected currency info */}
            {currencyInfo && (
              <div className="poe-panel rounded px-3 py-2">
                <div className="font-bold text-sm mb-1" style={{ color: "#c8a951" }}>
                  {currencyInfo.icon} {currencyInfo.name}
                </div>
                <div className="text-xs mb-1" style={{ color: "#888" }}>{currencyInfo.description}</div>
                {isCurrencyValid(currencyInfo.id) ? (
                  <span className="text-xs" style={{ color: "#44cc44" }}>✓ Применимо к текущему предмету</span>
                ) : (
                  <span className="text-xs" style={{ color: "#cc4444" }}>✗ Неприменимо ({session.rarity} предмет)</span>
                )}
              </div>
            )}

            {/* Auto-craft toggle */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="autoCraft"
                className="poe-checkbox"
                checked={autoCraft}
                onChange={(e) => setAutoCraft(e.target.checked)}
              />
              <label htmlFor="autoCraft" className="text-sm cursor-pointer" style={{ color: "#c8c8c8" }}>
                Авто-крафт до цели
              </label>
            </div>
            {autoCraft && (
              <div className="text-xs px-2 py-1 rounded" style={{ background: "rgba(200,169,81,0.08)", color: "#c8a951", border: "1px solid #3d2e0a" }}>
                ⚠️ Автоматически применяет валюту до 1000 раз или до достижения цели
              </div>
            )}

            {/* Craft Button */}
            <button
              onClick={handleCraft}
              disabled={loading || !selectedCurrency || (selectedCurrency ? !isCurrencyValid(selectedCurrency) : true)}
              className="poe-btn w-full py-3 text-base font-bold"
              style={{ letterSpacing: "0.05em" }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "#c8a951", borderTopColor: "transparent" }} />
                  Крафтим...
                </span>
              ) : autoCraft ? (
                "⚗️ Авто-крафт!"
              ) : (
                "⚗️ Применить"
              )}
            </button>

            {/* Recommendation */}
            <div className="poe-panel rounded px-3 py-2">
              <div className="text-xs font-bold mb-1" style={{ color: "#c8a951" }}>💡 Совет:</div>
              <div className="text-xs leading-relaxed" style={{ color: "#aaa" }}>{recommendation}</div>
            </div>

            {/* Currency spent */}
            {Object.keys(session.currencyUsed || {}).length > 0 && (
              <div>
                <div className="text-xs font-bold mb-2" style={{ color: "#888" }}>Потрачено валюты:</div>
                <div className="flex flex-col gap-1">
                  {Object.entries(session.currencyUsed || {}).map(([id, count]) => {
                    const currency = CURRENCIES.find((c) => c.id === id);
                    return (
                      <div key={id} className="flex items-center justify-between text-xs">
                        <span style={{ color: "#aaa" }}>
                          {currency?.icon} {currency?.name || id}
                        </span>
                        <span style={{ color: "#c8a951" }}>×{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
