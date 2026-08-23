"use client";

import { useState, useCallback } from "react";
import SessionManager from "./SessionManager";
import CraftingWorkbench from "./CraftingWorkbench";

export type Session = {
  id: number;
  name: string;
  itemBase: string;
  itemType: string;
  itemLevel: number;
  rarity: string;
  currentMods: RolledMod[];
  targetPrefixes: string[];
  targetSuffixes: string[];
  currencyUsed: Record<string, number>;
  attempts: number;
  isComplete: boolean;
  createdAt: string;
  updatedAt: string;
};

export type RolledMod = {
  modId: string;
  name: string;
  type: "prefix" | "suffix";
  category: string;
  description: string;
  tierName: string;
  tier: number;
  values: string;
  rolledValue: number;
};

export default function CraftingApp() {
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSessionSelect = useCallback((session: Session) => {
    setActiveSession(session);
  }, []);

  const handleSessionUpdate = useCallback((session: Session) => {
    setActiveSession(session);
    setRefreshKey((k) => k + 1);
  }, []);

  const handleSessionDelete = useCallback(() => {
    setActiveSession(null);
    setRefreshKey((k) => k + 1);
  }, []);

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundImage: "url('/images/poe-bg.jpg')", backgroundSize: "cover", backgroundAttachment: "fixed", backgroundPosition: "center" }}>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/75 pointer-events-none z-0" />

      {/* Header */}
      <header className="poe-header relative z-10 px-6 py-3 flex items-center gap-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl animate-glow">⚗️</span>
          <div>
            <h1 className="text-xl font-bold" style={{ color: "#c8a951", letterSpacing: "0.1em", textShadow: "0 0 10px rgba(200,169,81,0.5)" }}>
              PoE Craft Simulator
            </h1>
            <p className="text-xs" style={{ color: "#888" }}>Path of Exile — Крафт Симулятор</p>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-4 text-xs" style={{ color: "#888" }}>
          <span className="rarity-magic">◆ Магический</span>
          <span className="rarity-rare">◆ Редкий</span>
          <span style={{ color: "#af6025" }}>◆ Уникальный</span>
        </div>
      </header>

      {/* Main Layout */}
      <main className="relative z-10 flex flex-1 gap-4 p-4 max-w-screen-2xl mx-auto w-full">
        {/* Left: Sessions */}
        <aside className="w-72 flex-shrink-0">
          <SessionManager
            key={refreshKey}
            activeSessionId={activeSession?.id ?? null}
            onSessionSelect={handleSessionSelect}
            onSessionDelete={handleSessionDelete}
          />
        </aside>

        {/* Right: Workbench */}
        <div className="flex-1 min-w-0">
          {activeSession ? (
            <CraftingWorkbench
              session={activeSession}
              onUpdate={handleSessionUpdate}
            />
          ) : (
            <div className="poe-panel rounded p-12 flex flex-col items-center justify-center min-h-96 text-center">
              <span className="text-6xl mb-6 opacity-30">⚗️</span>
              <p className="text-2xl font-bold mb-2" style={{ color: "#c8a951" }}>Добро пожаловать в PoE Craft</p>
              <p className="text-sm" style={{ color: "#888", maxWidth: 400 }}>
                Создайте новую сессию крафта слева. Выберите базовый предмет, укажите уровень предмета, выберите нужные префиксы и суффиксы, затем крафтьте с помощью валюты.
              </p>
              <div className="mt-8 grid grid-cols-3 gap-4 text-center text-xs" style={{ color: "#666" }}>
                <div className="poe-panel p-3 rounded">
                  <div className="text-2xl mb-1">🔵</div>
                  <div>Transmutation</div>
                </div>
                <div className="poe-panel p-3 rounded">
                  <div className="text-2xl mb-1">🌀</div>
                  <div>Chaos Orb</div>
                </div>
                <div className="poe-panel p-3 rounded">
                  <div className="text-2xl mb-1">✨</div>
                  <div>Exalted Orb</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
