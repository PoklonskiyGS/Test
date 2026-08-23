"use client";

import { useState } from "react";
import { CURRENCIES } from "@/lib/poe-data";

type Props = {
  selectedCurrency: string | null;
  onSelect: (id: string) => void;
  isCurrencyValid: (id: string) => boolean;
  currencyUsed: Record<string, number>;
};

const CURRENCY_GROUPS = [
  {
    name: "Normal → Magic",
    currencies: ["orb_of_transmutation"],
  },
  {
    name: "Magic Crafting",
    currencies: ["orb_of_alteration", "orb_of_augmentation", "regal_orb"],
  },
  {
    name: "Normal → Rare",
    currencies: ["orb_of_alchemy"],
  },
  {
    name: "Rare Crafting",
    currencies: ["orb_of_chaos", "exalted_orb"],
  },
  {
    name: "Утилиты",
    currencies: ["orb_of_scouring", "annulment_orb", "divine_orb"],
  },
];

export default function CurrencyInventory({ selectedCurrency, onSelect, isCurrencyValid, currencyUsed }: Props) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const hoveredCurrency = CURRENCIES.find((c) => c.id === hoveredId);

  return (
    <div className="flex flex-col gap-3">
      {CURRENCY_GROUPS.map((group) => (
        <div key={group.name}>
          <div className="text-xs mb-1.5" style={{ color: "#555" }}>{group.name}</div>
          <div className="grid grid-cols-3 gap-2">
            {group.currencies.map((currId) => {
              const currency = CURRENCIES.find((c) => c.id === currId);
              if (!currency) return null;

              const isSelected = selectedCurrency === currId;
              const isValid = isCurrencyValid(currId);
              const usedCount = currencyUsed[currId] || 0;

              return (
                <div
                  key={currId}
                  onClick={() => isValid && onSelect(currId)}
                  onMouseEnter={() => setHoveredId(currId)}
                  onMouseLeave={() => setHoveredId(null)}
                  className={`currency-slot relative flex flex-col items-center justify-center rounded p-2 text-center ${isSelected ? "active" : ""}`}
                  style={{
                    background: isSelected
                      ? "rgba(200,169,81,0.15)"
                      : isValid
                      ? "rgba(255,255,255,0.03)"
                      : "rgba(0,0,0,0.3)",
                    border: `1px solid ${isSelected ? "#c8a951" : isValid ? "#2a1f08" : "#1a1208"}`,
                    opacity: isValid ? 1 : 0.4,
                    cursor: isValid ? "pointer" : "not-allowed",
                    minHeight: 70,
                  }}
                >
                  <span className="text-2xl leading-none mb-1">{currency.icon}</span>
                  <span
                    className="text-xs leading-tight"
                    style={{
                      color: isSelected ? "#c8a951" : isValid ? "#c8c8c8" : "#555",
                      fontSize: "0.62rem",
                      lineHeight: "1.1",
                    }}
                  >
                    {currency.name.replace("Orb of ", "").replace(" Orb", "").replace("Orb", "")}
                  </span>
                  {usedCount > 0 && (
                    <span
                      className="absolute top-1 right-1 text-xs font-bold leading-none"
                      style={{ color: "#c8a951", fontSize: "0.65rem" }}
                    >
                      ×{usedCount}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {/* Hovered tooltip */}
      {hoveredCurrency && (
        <div className="poe-tooltip rounded text-xs" style={{ background: "#1a1208", border: "1px solid #c8a951" }}>
          <div className="font-bold mb-1" style={{ color: "#c8a951" }}>
            {hoveredCurrency.icon} {hoveredCurrency.name}
          </div>
          <div style={{ color: "#c8c8c8" }}>{hoveredCurrency.description}</div>
        </div>
      )}
    </div>
  );
}
