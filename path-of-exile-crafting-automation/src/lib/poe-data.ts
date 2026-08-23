export type ModTier = {
  tier: number;
  name: string;
  values: string;
  minIlvl: number;
  weight: number;
};

export type PoEMod = {
  id: string;
  name: string;
  type: "prefix" | "suffix";
  category: string;
  description: string; // template like "+# to Maximum Life"
  tiers: ModTier[];
  tags: string[]; // weapon, armour, accessory, ring, amulet, belt, flask, etc.
};

export type Currency = {
  id: string;
  name: string;
  icon: string;
  description: string;
  action: string;
};

export type ItemBase = {
  id: string;
  name: string;
  type: string; // weapon, armour, accessory
  subType: string; // sword, helmet, ring, etc.
  tags: string[];
  implicits?: string[];
};

// ===== CURRENCY DATA =====
export const CURRENCIES: Currency[] = [
  {
    id: "orb_of_transmutation",
    name: "Orb of Transmutation",
    icon: "🔵",
    description: "Upgrades a Normal item to a Magic item",
    action: "transmute",
  },
  {
    id: "orb_of_alteration",
    name: "Orb of Alteration",
    icon: "🔄",
    description: "Reforges a Magic item with new random modifiers",
    action: "alteration",
  },
  {
    id: "orb_of_augmentation",
    name: "Orb of Augmentation",
    icon: "➕",
    description: "Adds a modifier to a Magic item that has only one modifier",
    action: "augmentation",
  },
  {
    id: "regal_orb",
    name: "Regal Orb",
    icon: "👑",
    description: "Upgrades a Magic item to a Rare item",
    action: "regal",
  },
  {
    id: "orb_of_chaos",
    name: "Orb of Chaos",
    icon: "🌀",
    description: "Reforges a Rare item with new random modifiers",
    action: "chaos",
  },
  {
    id: "exalted_orb",
    name: "Exalted Orb",
    icon: "✨",
    description: "Adds a new random modifier to a Rare item",
    action: "exalted",
  },
  {
    id: "orb_of_scouring",
    name: "Orb of Scouring",
    icon: "🧹",
    description: "Removes all modifiers from an item",
    action: "scour",
  },
  {
    id: "orb_of_alchemy",
    name: "Orb of Alchemy",
    icon: "⚗️",
    description: "Upgrades a Normal item to a Rare item",
    action: "alchemy",
  },
  {
    id: "annulment_orb",
    name: "Orb of Annulment",
    icon: "❌",
    description: "Removes a random modifier from an item",
    action: "annulment",
  },
  {
    id: "divine_orb",
    name: "Divine Orb",
    icon: "🌟",
    description: "Randomises the numeric values of the random modifiers on an item",
    action: "divine",
  },
];

// ===== ITEM BASES =====
export const ITEM_BASES: ItemBase[] = [
  // Weapons
  { id: "iron_sword", name: "Iron Sword", type: "weapon", subType: "sword", tags: ["weapon", "one_hand", "sword", "melee"] },
  { id: "long_sword", name: "Long Sword", type: "weapon", subType: "sword", tags: ["weapon", "one_hand", "sword", "melee"] },
  { id: "vaal_blade", name: "Vaal Blade", type: "weapon", subType: "sword", tags: ["weapon", "one_hand", "sword", "melee"] },
  { id: "karui_saber", name: "Karui Saber", type: "weapon", subType: "sword", tags: ["weapon", "one_hand", "sword", "melee"] },
  { id: "great_sword", name: "Great Sword", type: "weapon", subType: "sword", tags: ["weapon", "two_hand", "sword", "melee"] },
  { id: "driftwood_wand", name: "Driftwood Wand", type: "weapon", subType: "wand", tags: ["weapon", "one_hand", "wand", "caster"] },
  { id: "imbued_wand", name: "Imbued Wand", type: "weapon", subType: "wand", tags: ["weapon", "one_hand", "wand", "caster"] },
  { id: "void_sceptre", name: "Void Sceptre", type: "weapon", subType: "sceptre", tags: ["weapon", "one_hand", "sceptre", "caster"] },
  { id: "driftwood_maul", name: "Driftwood Maul", type: "weapon", subType: "mace", tags: ["weapon", "two_hand", "mace", "melee"] },
  { id: "karui_maul", name: "Karui Maul", type: "weapon", subType: "mace", tags: ["weapon", "two_hand", "mace", "melee"] },
  { id: "quiver", name: "Broadhead Arrow Quiver", type: "weapon", subType: "quiver", tags: ["weapon", "quiver", "ranged"] },
  // Armour
  { id: "leather_belt", name: "Leather Belt", type: "accessory", subType: "belt", tags: ["accessory", "belt"], implicits: ["+25-40 to maximum Life"] },
  { id: "rustic_sash", name: "Rustic Sash", type: "accessory", subType: "belt", tags: ["accessory", "belt"], implicits: ["12-24% increased Global Physical Damage"] },
  { id: "chain_belt", name: "Chain Belt", type: "accessory", subType: "belt", tags: ["accessory", "belt"], implicits: ["+9-20 to maximum Mana"] },
  { id: "iron_ring", name: "Iron Ring", type: "accessory", subType: "ring", tags: ["accessory", "ring"], implicits: ["+1-20 to Strength"] },
  { id: "coral_ring", name: "Coral Ring", type: "accessory", subType: "ring", tags: ["accessory", "ring"], implicits: ["+15-25 to maximum Life"] },
  { id: "sapphire_ring", name: "Sapphire Ring", type: "accessory", subType: "ring", tags: ["accessory", "ring"], implicits: ["+20-30% to Cold Resistance"] },
  { id: "topaz_ring", name: "Topaz Ring", type: "accessory", subType: "ring", tags: ["accessory", "ring"], implicits: ["+20-30% to Lightning Resistance"] },
  { id: "ruby_ring", name: "Ruby Ring", type: "accessory", subType: "ring", tags: ["accessory", "ring"], implicits: ["+20-30% to Fire Resistance"] },
  { id: "lapis_amulet", name: "Lapis Amulet", type: "accessory", subType: "amulet", tags: ["accessory", "amulet"], implicits: ["+16-25 to Intelligence"] },
  { id: "jade_amulet", name: "Jade Amulet", type: "accessory", subType: "amulet", tags: ["accessory", "amulet"], implicits: ["+20-30 to Dexterity"] },
  { id: "amber_amulet", name: "Amber Amulet", type: "accessory", subType: "amulet", tags: ["accessory", "amulet"], implicits: ["+20-30 to Strength"] },
  { id: "gold_amulet", name: "Gold Amulet", type: "accessory", subType: "amulet", tags: ["accessory", "amulet"] },
  // Helmets
  { id: "iron_hat", name: "Iron Hat", type: "armour", subType: "helmet", tags: ["armour", "helmet", "str_armour"] },
  { id: "vine_circlet", name: "Vine Circlet", type: "armour", subType: "helmet", tags: ["armour", "helmet", "int_armour"] },
  { id: "lion_pelt", name: "Lion Pelt", type: "armour", subType: "helmet", tags: ["armour", "helmet", "dex_armour"] },
  { id: "eternal_burgonet", name: "Eternal Burgonet", type: "armour", subType: "helmet", tags: ["armour", "helmet", "str_armour"] },
  // Body
  { id: "plate_vest", name: "Plate Vest", type: "armour", subType: "body", tags: ["armour", "body", "str_armour"] },
  { id: "scholar_robe", name: "Scholar's Robe", type: "armour", subType: "body", tags: ["armour", "body", "int_armour"] },
  { id: "crude_bow", name: "Crude Bow", type: "weapon", subType: "bow", tags: ["weapon", "two_hand", "bow", "ranged", "dex_weapon"] },
  // Gloves
  { id: "iron_gauntlets", name: "Iron Gauntlets", type: "armour", subType: "gloves", tags: ["armour", "gloves", "str_armour"] },
  { id: "wool_gloves", name: "Wool Gloves", type: "armour", subType: "gloves", tags: ["armour", "gloves", "int_armour"] },
  // Boots
  { id: "iron_greaves", name: "Iron Greaves", type: "armour", subType: "boots", tags: ["armour", "boots", "str_armour"] },
  { id: "wool_shoes", name: "Wool Shoes", type: "armour", subType: "boots", tags: ["armour", "boots", "int_armour"] },
  { id: "slink_boots", name: "Slink Boots", type: "armour", subType: "boots", tags: ["armour", "boots", "dex_armour"] },
];

// ===== MODS DATA =====
export const POE_MODS: PoEMod[] = [
  // ===== PREFIXES =====
  // Life
  {
    id: "of_the_lamprey",
    name: "Life",
    type: "prefix",
    category: "Life",
    description: "+# to maximum Life",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Crusade", values: "100-109", minIlvl: 84, weight: 500 },
      { tier: 2, name: "of the Boxer", values: "90-99", minIlvl: 78, weight: 600 },
      { tier: 3, name: "of the Athlete", values: "80-89", minIlvl: 72, weight: 700 },
      { tier: 4, name: "of the Wrestler", values: "70-79", minIlvl: 66, weight: 800 },
      { tier: 5, name: "of the Bear", values: "60-69", minIlvl: 58, weight: 900 },
      { tier: 6, name: "of the Ram", values: "50-59", minIlvl: 46, weight: 1000 },
      { tier: 7, name: "of the Ox", values: "40-49", minIlvl: 35, weight: 1100 },
      { tier: 8, name: "of the Deer", values: "30-39", minIlvl: 24, weight: 1200 },
    ],
  },
  // Energy Shield
  {
    id: "energy_shield_flat",
    name: "Energy Shield",
    type: "prefix",
    category: "Defence",
    description: "+# to maximum Energy Shield",
    tags: ["armour", "accessory"],
    tiers: [
      { tier: 1, name: "of the Radiant", values: "85-100", minIlvl: 80, weight: 400 },
      { tier: 2, name: "of the Shielded", values: "65-84", minIlvl: 68, weight: 500 },
      { tier: 3, name: "of the Warded", values: "45-64", minIlvl: 56, weight: 600 },
      { tier: 4, name: "of the Guarded", values: "30-44", minIlvl: 44, weight: 700 },
      { tier: 5, name: "of the Warded", values: "20-29", minIlvl: 30, weight: 800 },
    ],
  },
  // Physical Damage (weapons)
  {
    id: "physical_damage_pct",
    name: "Physical Damage %",
    type: "prefix",
    category: "Damage",
    description: "#% increased Physical Damage",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "Cruel", values: "170-179%", minIlvl: 83, weight: 300 },
      { tier: 2, name: "Merciless", values: "155-169%", minIlvl: 73, weight: 400 },
      { tier: 3, name: "Tyrannical", values: "140-154%", minIlvl: 62, weight: 500 },
      { tier: 4, name: "Flaring", values: "120-139%", minIlvl: 50, weight: 600 },
      { tier: 5, name: "Tempered", values: "100-119%", minIlvl: 38, weight: 700 },
      { tier: 6, name: "Annealed", values: "75-99%", minIlvl: 25, weight: 800 },
      { tier: 7, name: "Gleaming", values: "50-74%", minIlvl: 13, weight: 900 },
    ],
  },
  // Adds Physical Damage (weapons)
  {
    id: "adds_physical_damage",
    name: "Adds Physical Damage",
    type: "prefix",
    category: "Damage",
    description: "Adds #-# Physical Damage",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "Flaring", values: "19-26 to 36-45", minIlvl: 77, weight: 400 },
      { tier: 2, name: "Tempered", values: "14-20 to 27-38", minIlvl: 65, weight: 500 },
      { tier: 3, name: "Annealed", values: "11-15 to 21-29", minIlvl: 54, weight: 600 },
      { tier: 4, name: "Polished", values: "6-10 to 13-20", minIlvl: 36, weight: 700 },
      { tier: 5, name: "Burnished", values: "3-6 to 7-12", minIlvl: 13, weight: 800 },
    ],
  },
  // Adds Fire Damage (weapons)
  {
    id: "adds_fire_damage",
    name: "Adds Fire Damage",
    type: "prefix",
    category: "Damage",
    description: "Adds #-# Fire Damage",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "Cremating", values: "11-20 to 22-42", minIlvl: 76, weight: 350 },
      { tier: 2, name: "Incinerating", values: "8-15 to 17-35", minIlvl: 63, weight: 450 },
      { tier: 3, name: "Scorching", values: "6-11 to 12-25", minIlvl: 52, weight: 550 },
      { tier: 4, name: "Flaming", values: "4-7 to 8-16", minIlvl: 38, weight: 650 },
      { tier: 5, name: "Heated", values: "2-4 to 5-10", minIlvl: 20, weight: 750 },
    ],
  },
  // Adds Cold Damage (weapons)
  {
    id: "adds_cold_damage",
    name: "Adds Cold Damage",
    type: "prefix",
    category: "Damage",
    description: "Adds #-# Cold Damage",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "Glaciated", values: "10-14 to 20-24", minIlvl: 76, weight: 350 },
      { tier: 2, name: "Freezing", values: "7-11 to 15-19", minIlvl: 63, weight: 450 },
      { tier: 3, name: "Chilling", values: "5-8 to 11-14", minIlvl: 52, weight: 550 },
      { tier: 4, name: "Frosted", values: "3-5 to 7-9", minIlvl: 38, weight: 650 },
      { tier: 5, name: "Icy", values: "1-3 to 4-6", minIlvl: 20, weight: 750 },
    ],
  },
  // Adds Lightning Damage (weapons)
  {
    id: "adds_lightning_damage",
    name: "Adds Lightning Damage",
    type: "prefix",
    category: "Damage",
    description: "Adds #-# Lightning Damage",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "Electrocuting", values: "1-30 to 56-60", minIlvl: 76, weight: 350 },
      { tier: 2, name: "Discharging", values: "1-24 to 45-50", minIlvl: 63, weight: 450 },
      { tier: 3, name: "Shocking", values: "1-18 to 34-38", minIlvl: 52, weight: 550 },
      { tier: 4, name: "Sparkling", values: "1-13 to 25-28", minIlvl: 38, weight: 650 },
      { tier: 5, name: "Buzzing", values: "1-9 to 17-20", minIlvl: 20, weight: 750 },
    ],
  },
  // Spell Damage (wands/sceptres)
  {
    id: "spell_damage",
    name: "Spell Damage",
    type: "prefix",
    category: "Damage",
    description: "#% increased Spell Damage",
    tags: ["weapon", "caster"],
    tiers: [
      { tier: 1, name: "Spell Slinger's", values: "85-100%", minIlvl: 83, weight: 300 },
      { tier: 2, name: "Arcanist's", values: "65-84%", minIlvl: 73, weight: 400 },
      { tier: 3, name: "Invoker's", values: "45-64%", minIlvl: 55, weight: 500 },
      { tier: 4, name: "Caster's", values: "25-44%", minIlvl: 38, weight: 600 },
    ],
  },
  // Armour flat
  {
    id: "flat_armour",
    name: "Armour",
    type: "prefix",
    category: "Defence",
    description: "+# to Armour",
    tags: ["armour"],
    tiers: [
      { tier: 1, name: "Mammoth's", values: "600-799", minIlvl: 84, weight: 400 },
      { tier: 2, name: "Rhinoceros'", values: "450-599", minIlvl: 72, weight: 500 },
      { tier: 3, name: "Colossus'", values: "320-449", minIlvl: 60, weight: 600 },
      { tier: 4, name: "Titan's", values: "220-319", minIlvl: 48, weight: 700 },
      { tier: 5, name: "Giant's", values: "140-219", minIlvl: 36, weight: 800 },
      { tier: 6, name: "Golem's", values: "80-139", minIlvl: 24, weight: 900 },
    ],
  },
  // Evasion
  {
    id: "flat_evasion",
    name: "Evasion Rating",
    type: "prefix",
    category: "Defence",
    description: "+# to Evasion Rating",
    tags: ["armour"],
    tiers: [
      { tier: 1, name: "Ephemeral", values: "600-799", minIlvl: 84, weight: 400 },
      { tier: 2, name: "Vaporous", values: "450-599", minIlvl: 72, weight: 500 },
      { tier: 3, name: "Ghostly", values: "320-449", minIlvl: 60, weight: 600 },
      { tier: 4, name: "Flickering", values: "220-319", minIlvl: 48, weight: 700 },
      { tier: 5, name: "Shifting", values: "140-219", minIlvl: 36, weight: 800 },
    ],
  },
  // Mana
  {
    id: "flat_mana",
    name: "Maximum Mana",
    type: "prefix",
    category: "Mana",
    description: "+# to maximum Mana",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "Glimmering", values: "90-100", minIlvl: 84, weight: 500 },
      { tier: 2, name: "Glowing", values: "75-89", minIlvl: 72, weight: 600 },
      { tier: 3, name: "Shining", values: "60-74", minIlvl: 60, weight: 700 },
      { tier: 4, name: "Sparkling", values: "45-59", minIlvl: 46, weight: 800 },
      { tier: 5, name: "Glinting", values: "30-44", minIlvl: 30, weight: 900 },
      { tier: 6, name: "Glimmering", values: "20-29", minIlvl: 15, weight: 1000 },
    ],
  },
  // Attack Speed
  {
    id: "attack_speed",
    name: "Attack Speed",
    type: "prefix",
    category: "Attack",
    description: "#% increased Attack Speed",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "Blurred", values: "15-16%", minIlvl: 82, weight: 300 },
      { tier: 2, name: "Accelerating", values: "13-14%", minIlvl: 72, weight: 400 },
      { tier: 3, name: "Rapid", values: "11-12%", minIlvl: 60, weight: 500 },
      { tier: 4, name: "Quick", values: "8-10%", minIlvl: 40, weight: 600 },
      { tier: 5, name: "Brisk", values: "5-7%", minIlvl: 15, weight: 700 },
    ],
  },
  // Cast Speed
  {
    id: "cast_speed",
    name: "Cast Speed",
    type: "prefix",
    category: "Caster",
    description: "#% increased Cast Speed",
    tags: ["weapon", "caster"],
    tiers: [
      { tier: 1, name: "Thaumaturgical", values: "14-16%", minIlvl: 82, weight: 300 },
      { tier: 2, name: "Magician's", values: "11-13%", minIlvl: 68, weight: 400 },
      { tier: 3, name: "Priest's", values: "8-10%", minIlvl: 48, weight: 500 },
      { tier: 4, name: "Scholar's", values: "5-7%", minIlvl: 22, weight: 600 },
    ],
  },
  // Movement Speed (boots)
  {
    id: "movement_speed",
    name: "Movement Speed",
    type: "suffix",
    category: "Movement",
    description: "#% increased Movement Speed",
    tags: ["armour", "boots"],
    tiers: [
      { tier: 1, name: "of the Jaguar", values: "30%", minIlvl: 85, weight: 200 },
      { tier: 2, name: "of the Cheetah", values: "28%", minIlvl: 75, weight: 300 },
      { tier: 3, name: "of the Lynx", values: "25%", minIlvl: 65, weight: 400 },
      { tier: 4, name: "of the Fox", values: "20%", minIlvl: 50, weight: 500 },
      { tier: 5, name: "of the Rabbit", values: "15%", minIlvl: 32, weight: 600 },
      { tier: 6, name: "of the Tortoise", values: "10%", minIlvl: 10, weight: 700 },
    ],
  },

  // ===== SUFFIXES =====
  // Fire Resistance
  {
    id: "fire_resistance",
    name: "Fire Resistance",
    type: "suffix",
    category: "Resistance",
    description: "+#% to Fire Resistance",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Volcano", values: "36-40%", minIlvl: 66, weight: 800 },
      { tier: 2, name: "of the Furnace", values: "31-35%", minIlvl: 48, weight: 900 },
      { tier: 3, name: "of the Kiln", values: "26-30%", minIlvl: 36, weight: 1000 },
      { tier: 4, name: "of the Hearth", values: "21-25%", minIlvl: 24, weight: 1100 },
      { tier: 5, name: "of the Warming", values: "12-20%", minIlvl: 11, weight: 1200 },
      { tier: 6, name: "of the Embers", values: "6-11%", minIlvl: 1, weight: 1300 },
    ],
  },
  // Cold Resistance
  {
    id: "cold_resistance",
    name: "Cold Resistance",
    type: "suffix",
    category: "Resistance",
    description: "+#% to Cold Resistance",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Tundra", values: "36-40%", minIlvl: 66, weight: 800 },
      { tier: 2, name: "of the Glacier", values: "31-35%", minIlvl: 48, weight: 900 },
      { tier: 3, name: "of the Yeti", values: "26-30%", minIlvl: 36, weight: 1000 },
      { tier: 4, name: "of the Polar Bear", values: "21-25%", minIlvl: 24, weight: 1100 },
      { tier: 5, name: "of the Ice", values: "12-20%", minIlvl: 11, weight: 1200 },
      { tier: 6, name: "of the Sleet", values: "6-11%", minIlvl: 1, weight: 1300 },
    ],
  },
  // Lightning Resistance
  {
    id: "lightning_resistance",
    name: "Lightning Resistance",
    type: "suffix",
    category: "Resistance",
    description: "+#% to Lightning Resistance",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Lightning", values: "36-40%", minIlvl: 66, weight: 800 },
      { tier: 2, name: "of the Tempest", values: "31-35%", minIlvl: 48, weight: 900 },
      { tier: 3, name: "of the Thunder", values: "26-30%", minIlvl: 36, weight: 1000 },
      { tier: 4, name: "of the Storm", values: "21-25%", minIlvl: 24, weight: 1100 },
      { tier: 5, name: "of the Cloud", values: "12-20%", minIlvl: 11, weight: 1200 },
      { tier: 6, name: "of the Zap", values: "6-11%", minIlvl: 1, weight: 1300 },
    ],
  },
  // Chaos Resistance
  {
    id: "chaos_resistance",
    name: "Chaos Resistance",
    type: "suffix",
    category: "Resistance",
    description: "+#% to Chaos Resistance",
    tags: ["armour", "accessory"],
    tiers: [
      { tier: 1, name: "of the Order", values: "26-30%", minIlvl: 68, weight: 400 },
      { tier: 2, name: "of the Void", values: "21-25%", minIlvl: 56, weight: 500 },
      { tier: 3, name: "of the Shadows", values: "16-20%", minIlvl: 44, weight: 600 },
      { tier: 4, name: "of Warding", values: "11-15%", minIlvl: 30, weight: 700 },
      { tier: 5, name: "of the Uncertain", values: "6-10%", minIlvl: 15, weight: 800 },
    ],
  },
  // Attributes
  {
    id: "strength",
    name: "Strength",
    type: "suffix",
    category: "Attribute",
    description: "+# to Strength",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Titan", values: "46-50", minIlvl: 75, weight: 600 },
      { tier: 2, name: "of the Colossus", values: "41-45", minIlvl: 65, weight: 700 },
      { tier: 3, name: "of the Giant", values: "36-40", minIlvl: 55, weight: 800 },
      { tier: 4, name: "of the Goliath", values: "31-35", minIlvl: 44, weight: 900 },
      { tier: 5, name: "of the Ox", values: "26-30", minIlvl: 33, weight: 1000 },
      { tier: 6, name: "of the Bear", values: "21-25", minIlvl: 22, weight: 1100 },
      { tier: 7, name: "of the Ape", values: "16-20", minIlvl: 11, weight: 1200 },
      { tier: 8, name: "of Might", values: "8-15", minIlvl: 1, weight: 1300 },
    ],
  },
  {
    id: "dexterity",
    name: "Dexterity",
    type: "suffix",
    category: "Attribute",
    description: "+# to Dexterity",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Wind", values: "46-50", minIlvl: 75, weight: 600 },
      { tier: 2, name: "of the Phantom", values: "41-45", minIlvl: 65, weight: 700 },
      { tier: 3, name: "of the Falcon", values: "36-40", minIlvl: 55, weight: 800 },
      { tier: 4, name: "of the Fox", values: "31-35", minIlvl: 44, weight: 900 },
      { tier: 5, name: "of the Lynx", values: "26-30", minIlvl: 33, weight: 1000 },
      { tier: 6, name: "of the Cat", values: "21-25", minIlvl: 22, weight: 1100 },
      { tier: 7, name: "of the Mongoose", values: "16-20", minIlvl: 11, weight: 1200 },
      { tier: 8, name: "of Agility", values: "8-15", minIlvl: 1, weight: 1300 },
    ],
  },
  {
    id: "intelligence",
    name: "Intelligence",
    type: "suffix",
    category: "Attribute",
    description: "+# to Intelligence",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Polymath", values: "46-50", minIlvl: 75, weight: 600 },
      { tier: 2, name: "of the Sage", values: "41-45", minIlvl: 65, weight: 700 },
      { tier: 3, name: "of the Wizard", values: "36-40", minIlvl: 55, weight: 800 },
      { tier: 4, name: "of the Sorcerer", values: "31-35", minIlvl: 44, weight: 900 },
      { tier: 5, name: "of the Scholar", values: "26-30", minIlvl: 33, weight: 1000 },
      { tier: 6, name: "of the Mage", values: "21-25", minIlvl: 22, weight: 1100 },
      { tier: 7, name: "of the Student", values: "16-20", minIlvl: 11, weight: 1200 },
      { tier: 8, name: "of the Apprentice", values: "8-15", minIlvl: 1, weight: 1300 },
    ],
  },
  // Critical Strike Chance
  {
    id: "crit_chance",
    name: "Critical Strike Chance",
    type: "suffix",
    category: "Critical",
    description: "#% increased Critical Strike Chance",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "of Havoc", values: "35-38%", minIlvl: 78, weight: 300 },
      { tier: 2, name: "of Decimation", values: "30-34%", minIlvl: 64, weight: 400 },
      { tier: 3, name: "of Ruin", values: "25-29%", minIlvl: 52, weight: 500 },
      { tier: 4, name: "of Destruction", values: "20-24%", minIlvl: 40, weight: 600 },
      { tier: 5, name: "of Carnage", values: "15-19%", minIlvl: 25, weight: 700 },
      { tier: 6, name: "of Celebration", values: "10-14%", minIlvl: 10, weight: 800 },
    ],
  },
  // Critical Strike Multiplier
  {
    id: "crit_multiplier",
    name: "Critical Strike Multiplier",
    type: "suffix",
    category: "Critical",
    description: "+#% to Critical Strike Multiplier",
    tags: ["weapon", "accessory"],
    tiers: [
      { tier: 1, name: "of Glory", values: "35-38%", minIlvl: 78, weight: 300 },
      { tier: 2, name: "of Triumph", values: "30-34%", minIlvl: 64, weight: 400 },
      { tier: 3, name: "of Mastery", values: "25-29%", minIlvl: 52, weight: 500 },
      { tier: 4, name: "of Skill", values: "20-24%", minIlvl: 35, weight: 600 },
      { tier: 5, name: "of Talent", values: "15-19%", minIlvl: 20, weight: 700 },
    ],
  },
  // Elemental Resistances (all)
  {
    id: "all_resistances",
    name: "All Elemental Resistances",
    type: "suffix",
    category: "Resistance",
    description: "+#% to all Elemental Resistances",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of the Rainbow", values: "16-17%", minIlvl: 69, weight: 350 },
      { tier: 2, name: "of the Elements", values: "13-15%", minIlvl: 55, weight: 450 },
      { tier: 3, name: "of the Walrus", values: "10-12%", minIlvl: 35, weight: 550 },
      { tier: 4, name: "of the Prism", values: "6-9%", minIlvl: 12, weight: 650 },
    ],
  },
  // Life Regeneration
  {
    id: "life_regen",
    name: "Life Regeneration",
    type: "suffix",
    category: "Life",
    description: "Regenerate # Life per second",
    tags: ["armour", "accessory"],
    tiers: [
      { tier: 1, name: "of Recuperation", values: "10.5-12", minIlvl: 80, weight: 400 },
      { tier: 2, name: "of Restoration", values: "8.0-10.4", minIlvl: 68, weight: 500 },
      { tier: 3, name: "of Rejuvenation", values: "5.4-7.9", minIlvl: 56, weight: 600 },
      { tier: 4, name: "of Regrowth", values: "3.0-5.3", minIlvl: 36, weight: 700 },
      { tier: 5, name: "of Repair", values: "1.6-2.9", minIlvl: 20, weight: 800 },
    ],
  },
  // Mana Regen
  {
    id: "mana_regen",
    name: "Mana Regeneration",
    type: "suffix",
    category: "Mana",
    description: "#% increased Mana Regeneration Rate",
    tags: ["armour", "accessory", "weapon"],
    tiers: [
      { tier: 1, name: "of Overflowing", values: "60-70%", minIlvl: 72, weight: 400 },
      { tier: 2, name: "of Replenishing", values: "50-59%", minIlvl: 60, weight: 500 },
      { tier: 3, name: "of Renewal", values: "40-49%", minIlvl: 46, weight: 600 },
      { tier: 4, name: "of Mending", values: "30-39%", minIlvl: 30, weight: 700 },
      { tier: 5, name: "of Restoration", values: "20-29%", minIlvl: 15, weight: 800 },
    ],
  },
  // Accuracy (weapons)
  {
    id: "accuracy",
    name: "Accuracy Rating",
    type: "suffix",
    category: "Attack",
    description: "+# to Accuracy Rating",
    tags: ["weapon"],
    tiers: [
      { tier: 1, name: "of Perfection", values: "300-325", minIlvl: 80, weight: 400 },
      { tier: 2, name: "of Excellence", values: "220-299", minIlvl: 66, weight: 500 },
      { tier: 3, name: "of Distinction", values: "160-219", minIlvl: 55, weight: 600 },
      { tier: 4, name: "of Precision", values: "120-159", minIlvl: 44, weight: 700 },
      { tier: 5, name: "of Steadiness", values: "80-119", minIlvl: 30, weight: 800 },
      { tier: 6, name: "of Sureness", values: "40-79", minIlvl: 15, weight: 900 },
    ],
  },
  // Increased Rarity
  {
    id: "item_rarity",
    name: "Item Rarity",
    type: "suffix",
    category: "Utility",
    description: "#% increased Rarity of Items Found",
    tags: ["armour", "weapon", "accessory"],
    tiers: [
      { tier: 1, name: "of the Elder", values: "32-36%", minIlvl: 77, weight: 250 },
      { tier: 2, name: "of the Aristocrat", values: "26-31%", minIlvl: 60, weight: 350 },
      { tier: 3, name: "of the Noble", values: "20-25%", minIlvl: 40, weight: 450 },
      { tier: 4, name: "of the Collector", values: "12-19%", minIlvl: 24, weight: 550 },
    ],
  },
];

// ===== CRAFTING LOGIC HELPERS =====
export function getModsForItemType(itemBase: ItemBase, itemLevel: number): PoEMod[] {
  return POE_MODS.filter((mod) => {
    const hasTag = mod.tags.some((tag) => itemBase.tags.includes(tag));
    const hasValidTier = mod.tiers.some((tier) => tier.minIlvl <= itemLevel);
    return hasTag && hasValidTier;
  });
}

export function getAvailableTier(mod: PoEMod, itemLevel: number): ModTier | null {
  const validTiers = mod.tiers.filter((t) => t.minIlvl <= itemLevel);
  return validTiers.length > 0 ? validTiers[0] : null;
}

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

export function rollRandomValue(values: string): number {
  const match = values.match(/^([\d.]+)(?:-([\d.]+))?/);
  if (!match) return 0;
  const min = parseFloat(match[1]);
  const max = match[2] ? parseFloat(match[2]) : min;
  return Math.round((Math.random() * (max - min) + min) * 10) / 10;
}

export function rollMod(mod: PoEMod, itemLevel: number): RolledMod | null {
  const tier = getAvailableTier(mod, itemLevel);
  if (!tier) return null;
  return {
    modId: mod.id,
    name: mod.name,
    type: mod.type,
    category: mod.category,
    description: mod.description,
    tierName: tier.name,
    tier: tier.tier,
    values: tier.values,
    rolledValue: rollRandomValue(tier.values),
  };
}

export function weightedRandom<T extends { weight: number }>(items: T[]): T | null {
  if (items.length === 0) return null;
  const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);
  let rand = Math.random() * totalWeight;
  for (const item of items) {
    rand -= item.weight;
    if (rand <= 0) return item;
  }
  return items[items.length - 1];
}

export function rollModsForItem(
  availableMods: PoEMod[],
  itemLevel: number,
  count: number,
  existingMods: RolledMod[] = []
): RolledMod[] {
  const result: RolledMod[] = [...existingMods];
  const usedModIds = new Set(result.map((m) => m.modId));
  const prefixCount = result.filter((m) => m.type === "prefix").length;
  const suffixCount = result.filter((m) => m.type === "suffix").length;

  let remainingCount = count;
  let attempts = 0;
  const maxAttempts = 200;

  while (remainingCount > 0 && attempts < maxAttempts) {
    attempts++;
    const currentPrefixes = result.filter((m) => m.type === "prefix").length;
    const currentSuffixes = result.filter((m) => m.type === "suffix").length;

    const eligible = availableMods.filter((mod) => {
      if (usedModIds.has(mod.id)) return false;
      if (mod.type === "prefix" && currentPrefixes >= 3) return false;
      if (mod.type === "suffix" && currentSuffixes >= 3) return false;
      const tier = getAvailableTier(mod, itemLevel);
      return tier !== null;
    });

    if (eligible.length === 0) break;

    // Build weighted pool
    const weightedPool = eligible.map((mod) => {
      const tier = getAvailableTier(mod, itemLevel)!;
      return { mod, weight: tier.weight };
    });

    const chosen = weightedRandom(weightedPool);
    if (!chosen) break;

    const rolledMod = rollMod(chosen.mod, itemLevel);
    if (!rolledMod) continue;

    result.push(rolledMod);
    usedModIds.add(chosen.mod.id);
    remainingCount--;
  }

  return result;
}

export function determineModCount(rarity: "magic" | "rare"): number {
  if (rarity === "magic") {
    return Math.random() < 0.5 ? 1 : 2;
  }
  // rare: 4 (8/12), 5 (3/12), 6 (1/12)
  const roll = Math.random();
  if (roll < 4 / 12) return 6;
  if (roll < 7 / 12) return 5;
  return 4;
}

export function formatDescription(description: string, values: string, rolledValue: number): string {
  const firstVal = rolledValue;
  return description.replace("#", String(firstVal));
}

export const CURRENCY_DESCRIPTIONS: Record<string, { steps: string[] }> = {
  orb_of_transmutation: {
    steps: ["Item is Normal → Magic", "Adds 1-2 random modifiers"],
  },
  orb_of_alteration: {
    steps: ["Rerolls all modifiers on a Magic item", "Adds 1-2 new random modifiers"],
  },
  orb_of_augmentation: {
    steps: ["Adds 1 modifier to a Magic item with only 1 modifier"],
  },
  regal_orb: {
    steps: ["Item upgrades: Magic → Rare", "Adds 1 additional random modifier"],
  },
  orb_of_chaos: {
    steps: ["Rerolls all modifiers on a Rare item", "Rolls 4-6 new random modifiers"],
  },
  exalted_orb: {
    steps: ["Adds 1 random modifier to a Rare item (must have open affix slots)"],
  },
  orb_of_scouring: {
    steps: ["Removes all modifiers", "Item reverts to Normal rarity"],
  },
  orb_of_alchemy: {
    steps: ["Item is Normal → Rare", "Adds 4-6 random modifiers"],
  },
  annulment_orb: {
    steps: ["Removes 1 random modifier from a Magic or Rare item"],
  },
  divine_orb: {
    steps: ["Rerrolls the numeric values of all modifiers", "Tiers and mod types stay the same"],
  },
};
