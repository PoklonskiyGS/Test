import {
  RolledMod,
  rollModsForItem,
  determineModCount,
  rollRandomValue,
  getModsForItemType,
  ITEM_BASES,
  rollMod,
  weightedRandom,
  getAvailableTier,
} from "./poe-data";

export type ItemState = {
  base: string;
  itemLevel: number;
  rarity: "normal" | "magic" | "rare";
  mods: RolledMod[];
};

export type CraftResult = {
  before: ItemState;
  after: ItemState;
  currency: string;
  success: boolean;
  message: string;
};

function getItemBase(baseId: string) {
  return ITEM_BASES.find((b) => b.id === baseId) || ITEM_BASES[0];
}

export function applyCurrency(state: ItemState, currencyId: string): CraftResult {
  const before: ItemState = JSON.parse(JSON.stringify(state));
  const itemBase = getItemBase(state.base);
  const availableMods = getModsForItemType(itemBase, state.itemLevel);

  let after: ItemState = JSON.parse(JSON.stringify(state));
  let message = "";
  let success = true;

  switch (currencyId) {
    case "orb_of_transmutation": {
      if (state.rarity !== "normal") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Normal items" };
      }
      const count = determineModCount("magic");
      const mods = rollModsForItem(availableMods, state.itemLevel, count, []);
      after = { ...state, rarity: "magic", mods };
      message = `Transmuted to Magic with ${mods.length} modifier(s)`;
      break;
    }

    case "orb_of_alteration": {
      if (state.rarity !== "magic") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Magic items" };
      }
      const count = determineModCount("magic");
      const mods = rollModsForItem(availableMods, state.itemLevel, count, []);
      after = { ...state, mods };
      message = `Altered: ${mods.length} new modifier(s)`;
      break;
    }

    case "orb_of_augmentation": {
      if (state.rarity !== "magic") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Magic items" };
      }
      if (state.mods.length >= 2) {
        return { before, after, currency: currencyId, success: false, message: "Magic item already has 2 modifiers" };
      }
      const mods = rollModsForItem(availableMods, state.itemLevel, 1, state.mods);
      after = { ...state, mods };
      message = `Augmented: added 1 new modifier`;
      break;
    }

    case "regal_orb": {
      if (state.rarity !== "magic") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Magic items" };
      }
      const mods = rollModsForItem(availableMods, state.itemLevel, 1, state.mods);
      after = { ...state, rarity: "rare", mods };
      message = `Regaled to Rare: added 1 more modifier`;
      break;
    }

    case "orb_of_chaos": {
      if (state.rarity !== "rare") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Rare items" };
      }
      const count = determineModCount("rare");
      const mods = rollModsForItem(availableMods, state.itemLevel, count, []);
      after = { ...state, mods };
      message = `Chaos reroll: ${mods.length} new modifier(s)`;
      break;
    }

    case "orb_of_alchemy": {
      if (state.rarity !== "normal") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Normal items" };
      }
      const count = determineModCount("rare");
      const mods = rollModsForItem(availableMods, state.itemLevel, count, []);
      after = { ...state, rarity: "rare", mods };
      message = `Alchemied to Rare with ${mods.length} modifier(s)`;
      break;
    }

    case "exalted_orb": {
      if (state.rarity !== "rare") {
        return { before, after, currency: currencyId, success: false, message: "Can only use on Rare items" };
      }
      const prefixes = state.mods.filter((m) => m.type === "prefix").length;
      const suffixes = state.mods.filter((m) => m.type === "suffix").length;
      if (prefixes >= 3 && suffixes >= 3) {
        return { before, after, currency: currencyId, success: false, message: "Item has no open affix slots" };
      }
      const mods = rollModsForItem(availableMods, state.itemLevel, 1, state.mods);
      after = { ...state, mods };
      message = `Exalted: added 1 modifier (total: ${mods.length})`;
      break;
    }

    case "orb_of_scouring": {
      if (state.rarity === "normal") {
        return { before, after, currency: currencyId, success: false, message: "Item is already Normal" };
      }
      after = { ...state, rarity: "normal", mods: [] };
      message = `Scoured to Normal: all modifiers removed`;
      break;
    }

    case "annulment_orb": {
      if (state.mods.length === 0) {
        return { before, after, currency: currencyId, success: false, message: "Item has no modifiers to remove" };
      }
      const idx = Math.floor(Math.random() * state.mods.length);
      const removed = state.mods[idx];
      const mods = state.mods.filter((_, i) => i !== idx);
      let rarity = state.rarity;
      if (mods.length === 0) rarity = "normal";
      else if (mods.length <= 2 && state.rarity === "rare") rarity = "magic";
      after = { ...state, rarity, mods };
      message = `Annulled: removed "${removed.name}" (${removed.type})`;
      break;
    }

    case "divine_orb": {
      if (state.mods.length === 0) {
        return { before, after, currency: currencyId, success: false, message: "Item has no modifiers to divine" };
      }
      const mods = state.mods.map((mod) => ({
        ...mod,
        rolledValue: rollRandomValue(mod.values),
      }));
      after = { ...state, mods };
      message = `Divined: all modifier values re-rolled`;
      break;
    }

    default:
      return { before, after, currency: currencyId, success: false, message: "Unknown currency" };
  }

  return { before, after, currency: currencyId, success, message };
}

export function checkTargetMet(currentMods: RolledMod[], targetPrefixes: string[], targetSuffixes: string[]): boolean {
  if (targetPrefixes.length === 0 && targetSuffixes.length === 0) return false;

  const currentModIds = currentMods.map((m) => m.modId);

  const allPrefixesMet = targetPrefixes.every((id) => currentModIds.includes(id));
  const allSuffixesMet = targetSuffixes.every((id) => currentModIds.includes(id));

  return allPrefixesMet && allSuffixesMet;
}

export function getCraftingRecommendation(
  state: ItemState,
  targetPrefixes: string[],
  targetSuffixes: string[]
): string {
  const allTargets = [...targetPrefixes, ...targetSuffixes];
  if (allTargets.length === 0) return "Select target modifiers to get crafting advice";

  const currentModIds = state.mods.map((m) => m.modId);
  const missingTargets = allTargets.filter((id) => !currentModIds.includes(id));

  if (missingTargets.length === 0) return "✅ All target modifiers are present!";

  const prefixes = state.mods.filter((m) => m.type === "prefix").length;
  const suffixes = state.mods.filter((m) => m.type === "suffix").length;

  if (state.rarity === "normal") {
    if (allTargets.length <= 2) {
      return "💡 Use Orb of Transmutation to make Magic, then Alteration spam";
    }
    return "💡 Use Orb of Alchemy to make Rare, then Chaos Orb spam";
  }

  if (state.rarity === "magic") {
    return "💡 Spam Orb of Alteration until you hit your target modifiers, then Regal Orb";
  }

  if (state.rarity === "rare") {
    const missingPrefixes = targetPrefixes.filter((id) => !currentModIds.includes(id));
    const missingSuffixes = targetSuffixes.filter((id) => !currentModIds.includes(id));

    if (missingPrefixes.length > 0 && missingSuffixes.length > 0) {
      return "💡 Use Orb of Chaos to reroll all modifiers";
    }

    if (missingPrefixes.length > 0 && prefixes < 3) {
      return "💡 Use Exalted Orb to add a prefix (open prefix slots available)";
    }

    if (missingSuffixes.length > 0 && suffixes < 3) {
      return "💡 Use Exalted Orb to add a suffix (open suffix slots available)";
    }

    return "💡 Use Orb of Chaos to reroll all modifiers";
  }

  return "Select modifiers and currency to craft";
}
