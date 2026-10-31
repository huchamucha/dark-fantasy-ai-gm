export type AttributeId =
  | "strength"
  | "dexterity"
  | "constitution"
  | "intelligence"
  | "wisdom"
  | "charisma";

export type AttributeDefinition = {
  id: AttributeId;
  name: string;
  description: string;
};

export type SkillDefinition = {
  id: string;
  name: string;
  description: string;
  ability: AttributeId;
};

export type CharacterAttributes = Record<AttributeId, number>;

export type Character = {
  id: string;
  name: string;
  class_name: string;
  level: number;
  hp: number;
  max_hp: number;
} & CharacterAttributes;

export type StoryPack = {
  id: string;
  name: string;
  description: string;
  status: string;
};

export type TurnResponse = {
  turn_id: string;
  narrative: string;
  outcome: string;
  summary: string;
  hp_change: number;
  stat_changes: Record<string, number>;
  inventory_changes: Array<Record<string, unknown>>;
  quest_updates: Array<Record<string, unknown>>;
  npc_updates: Array<Record<string, unknown>>;
  world_flags: Record<string, unknown>;
  next_scene_hint: string;
};