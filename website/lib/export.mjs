/** Serialize tabular values without changing missing values or embedded punctuation. */
export function serializeCsv(headers, rows) {
  const cell = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return [headers.join(','), ...rows.map(row => row.map(cell).join(','))].join('\r\n');
}
/** Serialize the selected records and keep nulls and source-role metadata intact. */
export function serializeJson(records) {
  return JSON.stringify({paperDataVersion:'2026-10-30',snapshot:'2026-10-15',note:'Historical configuration-level selections. Source roles can differ; source resolution does not establish execution completion or final-artifact identity.',records}, null, 2);
}
