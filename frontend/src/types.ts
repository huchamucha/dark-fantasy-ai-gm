export type Character = {
  id: string;
  name: string;
  class_name: string;
  hp: number;
  max_hp: number;
  strength: number;
  agility: number;
  intellect: number;
  will: number;
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
