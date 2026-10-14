// Star colours: each entity type always gets the same colour.
const PALETTE = ["#7dd3fc", "#f9a8d4", "#fcd34d", "#86efac", "#c4b5fd", "#fdba74", "#5eead4", "#fca5a5"];

export function colorForType(type = "") {
  let hash = 0;
  for (const char of type) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return PALETTE[hash % PALETTE.length];
}
