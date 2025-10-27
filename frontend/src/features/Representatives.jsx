import { createResource, Show, createSignal, createMemo } from "solid-js";
import { VirtualList } from "@solid-primitives/virtual";

async function fetchRepresentatives() {
  const res = await fetch("/fonts/representative", { cache: "no-store" });
  if (!res.ok) throw new Error("failed to load representatives");
  return res.json();
}

export default function Representatives() {
  const [representatives] = createResource(fetchRepresentatives);
  const [search, setSearch] = createSignal("");

  // Track which families were loaded to avoid re-loading
  const [loadedFamilies, setLoadedFamilies] = createSignal(new Set());

  const ensureFontLoaded = async (rep) => {
    if (!rep) return;
    const fam = rep.family || rep.full_name;
    if (!fam) return;

    const loaded = loadedFamilies();
    if (loaded.has(fam)) return;

    try {
      const filename = (rep.path?.split(/[\\\/]/).pop() || "");
      const base = filename.replace(/\.[^.]+$/, "");
      const url = `/api/fonts/${encodeURI(base)}.woff2`;
      const face = new FontFace(fam, `url(${url})`);
      const loadedFace = await face.load();
      document.fonts.add(loadedFace);
      const next = new Set(loaded);
      next.add(fam);
      setLoadedFamilies(next);
    } catch (_e) {
      // ignore load errors to keep the UI responsive
    }
  };


  const filteredRepresentatives = createMemo(() => {
    const reps = representatives() || [];
    const q = (search() || "").trim().toLowerCase();
    if (!q) return reps;

    const filtered = reps.filter(f => {
      const fam = (f.family || "").toLowerCase();
      return fam.includes(q);
    });
    console.log(filtered)
    return filtered;
  });

  return (
    <section style={{ padding: "1rem", width: "100%", margin: "0 auto" }}>
      <h2>Representative Fonts</h2>
      <input
        type="search"
        name="search"
        id="search"
        placeholder="Search families…"
        value={search()}
        onInput={(e) => setSearch(e.target.value)}
        style={{ width: "100%", padding: "8px 10px", margin: "0 0 12px 0" }}
      />

      <Show when={!representatives.loading} fallback={<p>Loading…</p>}>
        <Show when={!representatives.error} fallback={<p>Error loading representatives.</p>}>
          <VirtualList
            key={filteredRepresentatives().length}
            each={filteredRepresentatives()}
            rootHeight={560}
            rowHeight={48}
            overscanCount={10}
            fallback={<div>No fonts</div>}
          >
            {(f) => {
              // Kick off font loading when row renders (i.e., is visible)
              ensureFontLoaded(f);
              return (
                <div
                  style={{
                    height: "3rem",
                    display: "flex",
                    "align-items": "center",
                    padding: "16px",
                    "font-family": f.family,
                    "font-size": "2rem",
                    "line-height": "3rem",
                    width: "100%",
                    "white-space": "nowrap",
                    "overflow": "hidden",
                    "text-overflow": "ellipsis",
                  }}
                  title={f.full_name || f.family}
                >
                  {f.family || f.full_name || "(Unnamed)"}
                </div>
              );
            }}
          </VirtualList>
        </Show>
      </Show>
    </section>
  );
}
