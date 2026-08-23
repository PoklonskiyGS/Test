import { pgTable, serial, text, integer, jsonb, timestamp, boolean } from "drizzle-orm/pg-core";

export const craftingSessions = pgTable("crafting_sessions", {
  id: serial("id").primaryKey(),
  name: text("name").notNull().default("Unnamed Session"),
  itemBase: text("item_base").notNull(),
  itemType: text("item_type").notNull(), // weapon, armour, accessory, flask
  itemLevel: integer("item_level").notNull().default(80),
  rarity: text("rarity").notNull().default("normal"), // normal, magic, rare
  currentMods: jsonb("current_mods").notNull().default([]),
  targetPrefixes: jsonb("target_prefixes").notNull().default([]),
  targetSuffixes: jsonb("target_suffixes").notNull().default([]),
  currencyUsed: jsonb("currency_used").notNull().default({}),
  attempts: integer("attempts").notNull().default(0),
  isComplete: boolean("is_complete").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const craftingHistory = pgTable("crafting_history", {
  id: serial("id").primaryKey(),
  sessionId: integer("session_id").notNull().references(() => craftingSessions.id, { onDelete: "cascade" }),
  currency: text("currency").notNull(),
  modsBefore: jsonb("mods_before").notNull().default([]),
  modsAfter: jsonb("mods_after").notNull().default([]),
  rarityBefore: text("rarity_before").notNull(),
  rarityAfter: text("rarity_after").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
