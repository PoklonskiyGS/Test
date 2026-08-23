"use client";

import { useState, useEffect, useCallback } from "react";
import type { Session } from "./CraftingApp";
import { ITEM_BASES, POE_MODS } from "@/lib/poe-data";

type Props = {
  activeSessionId: number | null;
  onSessionSelect: (session: Session) => void;
  onSessionDelete: () => void;
};

export default function SessionManager({ activeSessionId, onSessionSelect, onSessionDelete }: Props) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: "",
    itemBase: ITEM_BASES[0].id,
    itemLevel: 80,
  });

  const fetchSessions = useCallback(async () => {
    const res = await fetch("/api/sessions");
    if (res.ok) {
      const data = await res.json();
      setSessions(data);
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleCreate = async () => {
    setLoading(true);
    const base = ITEM_BASES.find((b) => b.id === createForm.itemBase)!;
    const res = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: createForm.name || `Сессия: ${base.name}`,
        itemBase: createForm.itemBase,
        itemType: base.type,
        itemLevel: createForm.itemLevel,
        targetPrefixes: [],
        targetSuffixes: [],
      }),
    });
    if (res.ok) {
      const session = await res.json();
      await fetchSessions();
      onSessionSelect(session);
      setShowCreate(false);
      setCreateForm({ name: "", itemBase: ITEM_BASES[0].id, itemLevel: 80 });
    }
    setLoading(false);
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Удалить сессию?")) return;
    await fetch(`/api/sessions/${id}`, { method: "DELETE" });
    await fetchSessions();
    if (activeSessionId === id) onSessionDelete();
  };

  const getRarityColor = (rarity: string) => {
    if (rarity === "magic") return "#8888ff";
    if (rarity === "rare") return "#ffff77";
    return "#c8c8c8";
  };

  return (
    <div className="poe-panel rounded flex flex-col gap-0 overflow-hidden" style={{ minHeight: 500 }}>
      {/* Header */}
      <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: "1px solid #3d2e0a" }}>
        <span className="font-bold text-sm" style={{ color: "#c8a951" }}>📋 Сессии крафта</span>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="poe-btn text-xs px-3 py-1"
        >
          {showCreate ? "✕" : "+ Новая"}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="px-4 py-3 flex flex-col gap-3" style={{ borderBottom: "1px solid #3d2e0a", background: "#0d0a02" }}>
          <div>
            <label className="text-xs mb-1 block" style={{ color: "#888" }}>Название сессии</label>
            <input
              className="poe-input text-sm"
              placeholder="Моя сессия..."
              value={createForm.name}
              onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="text-xs mb-1 block" style={{ color: "#888" }}>Базовый предмет</label>
            <select
              className="poe-select text-sm"
              value={createForm.itemBase}
              onChange={(e) => setCreateForm((f) => ({ ...f, itemBase: e.target.value }))}
            >
              {Object.entries(
                ITEM_BASES.reduce((acc, base) => {
                  const key = `${base.type} — ${base.subType}`;
                  if (!acc[key]) acc[key] = [];
                  acc[key].push(base);
                  return acc;
                }, {} as Record<string, typeof ITEM_BASES>)
              ).map(([group, bases]) => (
                <optgroup key={group} label={group}>
                  {bases.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs mb-1 block" style={{ color: "#888" }}>Уровень предмета (iLvl): {createForm.itemLevel}</label>
            <input
              type="range"
              min={1}
              max={100}
              value={createForm.itemLevel}
              onChange={(e) => setCreateForm((f) => ({ ...f, itemLevel: parseInt(e.target.value) }))}
              className="w-full"
              style={{ accentColor: "#c8a951" }}
            />
          </div>
          <button
            onClick={handleCreate}
            disabled={loading}
            className="poe-btn poe-btn-success w-full"
          >
            {loading ? "Создание..." : "✓ Создать сессию"}
          </button>
        </div>
      )}

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className="p-6 text-center text-sm" style={{ color: "#555" }}>
            Нет сессий.<br />Создайте первую!
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            const base = ITEM_BASES.find((b) => b.id === session.itemBase);
            return (
              <div
                key={session.id}
                onClick={() => onSessionSelect(session)}
                className="px-4 py-3 cursor-pointer flex items-start justify-between gap-2 transition-colors"
                style={{
                  borderBottom: "1px solid #1f1505",
                  background: isActive ? "rgba(200,169,81,0.08)" : "transparent",
                  borderLeft: isActive ? "3px solid #c8a951" : "3px solid transparent",
                }}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {session.isComplete && <span className="text-xs text-green-400">✅</span>}
                    <span
                      className="text-sm font-semibold truncate"
                      style={{ color: getRarityColor(session.rarity) }}
                    >
                      {session.name}
                    </span>
                  </div>
                  <div className="text-xs" style={{ color: "#888" }}>
                    {base?.name || session.itemBase} • iLvl {session.itemLevel}
                  </div>
                  <div className="text-xs mt-1" style={{ color: "#666" }}>
                    <span className="capitalize" style={{ color: getRarityColor(session.rarity) }}>
                      {session.rarity === "normal" ? "Обычный" : session.rarity === "magic" ? "Магический" : "Редкий"}
                    </span>
                    {" · "}
                    {session.attempts} попыток
                    {" · "}
                    {session.currentMods?.length || 0} модов
                  </div>
                </div>
                <button
                  onClick={(e) => handleDelete(session.id, e)}
                  className="text-xs opacity-40 hover:opacity-100 flex-shrink-0 mt-1"
                  style={{ color: "#cc4444" }}
                  title="Удалить"
                >
                  ✕
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
