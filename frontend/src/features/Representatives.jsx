import { createResource, For, createEffect, Show } from "solid-js";

async function fetchRepresentatives() {
  const res = await fetch("/fonts/representative");
  if (!res.ok) throw new Error("failed to load representatives");
  return res.json();
}

export default function Representatives() {
  const [representatives] = createResource(fetchRepresentatives);

  createEffect(() => {
    const reps = representatives();
    if (!reps) return;


    reps.forEach(rep => {
      // Build the subset filename from the original file's basename (no extension)
      const base = rep.path.split("\\").at(-1).split(".").at(0);
      const url = `/api/fonts/${encodeURI(base)}.woff2`;
      const fontFace = new FontFace(rep.family, `url(${url})`);
      if (fontFace) fontFace.load().then(loadedFace => {
        document.fonts.add(loadedFace);
        console.log("Font loaded:", loadedFace.family);
      });
    });
  });

  return (
    <section style={{ padding: "1rem", "max-width": "800px", margin: "0 auto" }}>
      <h2>Representative Fonts</h2>

      <Show when={!representatives.loading} fallback={<p>Loading…</p>}>
        <Show when={!representatives.error} fallback={<p>Error loading representatives.</p>}>
          <ul>
            <For each={representatives() || []}>
              {(f) => (
                <li
                  style={{
                    "font-family": f.family
                  }}>
                  
                  {f.family || f.full_name || "(Unnamed)"}
                </li>
              )}
            </For>
          </ul>
        </Show>
      </Show>
    </section>
  );
}
