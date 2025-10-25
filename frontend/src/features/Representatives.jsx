import { createResource, createSignal, For, Show } from "solid-js";

async function fetchRepresentatives() {
  const res = await fetch("/fonts/representative");
  if (!res.ok) throw new Error("failed to load representatives");
  return res.json();
}

async function fetchFamily(id) {
  if (!id) return [];
  const res = await fetch(`/fonts/family/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("failed to load family");
  return res.json();
}

export default function Representatives() {
  const [selectedId, setSelectedId] = createSignal(null);
  const [representatives] = createResource(fetchRepresentatives);
  const [family] = createResource(selectedId, fetchFamily);

  return (
    <section style={{ padding: "1rem", "max-width": "800px", margin: "0 auto" }}>
      <h2>Representative Fonts</h2>

      <Show when={!representatives.loading} fallback={<p>Loading…</p>}>
        <Show when={!representatives.error} fallback={<p>Error loading representatives.</p>}>
          <ul style={{ display: "grid", gap: "0.5rem", "grid-template-columns": "repeat(auto-fill, minmax(220px, 1fr))" }}>
            <For each={representatives() || []}>
              {(f) => (
                <li style={{ border: "1px solid #ddd", padding: "0.5rem", cursor: "pointer" }}
                    onClick={() => setSelectedId(f.id)}>
                  <strong>{f.family || f.full_name || "(Unnamed)"}</strong>
                  <div style={{ color: "#666" }}>{f.style_name || ""}</div>
                  <div title={f.path} style={{ "font-size": "0.8rem", color: "#999", overflow: "hidden", "text-overflow": "ellipsis" }}>{f.path?.split("\\").at(-1)}</div>
                </li>
              )}
            </For>
          </ul>
        </Show>
      </Show>

      <Show when={selectedId()}>
        <h3 style={{ margin: "1rem 0 0.5rem" }}>Family</h3>
        <Show when={!family.loading} fallback={<p>Loading family…</p>}>
          <Show when={!family.error} fallback={<p>Error loading family.</p>}>
            <ul style={{ display: "grid", gap: "0.5rem", "grid-template-columns": "repeat(auto-fill, minmax(220px, 1fr))" }}>
              <For each={family() || []}>
                {(f) => (
                  <li style={{ border: "1px solid #eee", padding: "0.5rem", background: f.representative ? "#f9f9f9" : "white" }}>
                    <div><strong>{f.full_name || f.family}</strong></div>
                    <div style={{ color: "#666" }}>{f.style_name || ""}</div>
                    <div title={f.path} style={{ "font-size": "0.8rem", color: "#999", overflow: "hidden", "text-overflow": "ellipsis" }}>{f.path?.split("\\").at(-1)}</div>
                  </li>
                )}
              </For>
            </ul>
          </Show>
        </Show>
      </Show>
    </section>
  );
}

