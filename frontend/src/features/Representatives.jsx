import { createResource, createSignal, createMemo, onMount, onCleanup, Show, For, createRenderEffect, } from "solid-js";
import "../styles/representatives.css"

const loadedFonts = new Set();

async function loadFont(font) {
  if (!font || loadedFonts.has(font)) return;
  if (typeof document === "undefined" || typeof FontFace === "undefined") return;
  try {
    if (document.fonts && document.fonts.check(`1em "${font}"`)) {
      loadedFonts.add(font);
    }
  } catch {
    throw new Error("pas de fetch")
  }

  const face = new FontFace(font, `url(/api/fonts/${font.replaceAll(" ", "-")}.woff2)`);
  await face.load();
  document.fonts?.add(face);
  loadedFonts.add(font);
}

async function fetchRepresentatives() {
  const res = await fetch("/fonts/representative", { cache: "no-store" });
  if (!res.ok) throw new Error("failed to load representatives");
  return res.json();
}

async function fetchFamily(family) {
  if (!family.id) return
  const res = await fetch(`/fonts/family/${family.id}`)
  if (!res.ok) throw new Error("failed to load family content")
  return res.json()
}

export default function Representatives() {
  const [family, setFamily] = createSignal(null);
  const [search, setSearch] = createSignal("");
  const [text, setText] = createSignal("The quick brown fox jumps over the lazy dogs")
  const [familyData] = createResource(family, fetchFamily)
  const [representatives] = createResource(fetchRepresentatives);
  let time

  function handleQuery(value) {
    if (time) clearTimeout(time)
    time = setTimeout(() => setSearch(value), 100);
  }

  const filteredFonts = createMemo(() => {
    const data = representatives() ?? [];
    const term = search().trim().toLowerCase();
    if (!term) return data;
    return data.filter((font) => font.name.toLowerCase().includes(term));
  });


  return (
    <section id="font-viewer">
      <input
        type="search"
        placeholder="Search fonts..."
        onInput={(event) => handleQuery(event.currentTarget.value)}
      />
      <Show when={!representatives.error} fallback={<p style={{ color: "var(--danger-6)" }}>Unable to load fonts.</p>}>
        <Show when={!representatives.loading} fallback={<p>Loading fonts...</p>}>
          <List
            fonts={filteredFonts()}
            buffer={3}
            onSelect={(data) => setFamily(data)}
            text={text}
          />
        </Show>
      </Show>
      <input
        type="text"
        name="Pangram"
        id="Pangram"
        placeholder="The quick brown fox jumps over the lazy dog"
        onInput={(e) => setText(e.currentTarget.value)}
      />
      <section popover id="font-modal">
        <Show when={!familyData.error} fallback="grosse erreur salllllllllll">
          <Show when={!familyData.loading && family() !== null} fallback="chargementttttttttt">
            <h1>{family().name}</h1>
            <ul>
              <For each={familyData()}>
                {(font) => <li>{font.full_name}</li>}
              </For>
            </ul>
          </Show>
        </Show>

      </section>
    </section>
  );
}

function List(props) {
  const [itemHeight, setItemHeight] = createSignal(100)
  const [containerHeight, setContainerHeight] = createSignal(0)
  const [scroll, setScroll] = createSignal(0)
  let containerREF


  const visibleCount = createMemo(() => Math.ceil(containerHeight() / itemHeight()) + props.buffer * 2);
  const startIndex = createMemo(() => Math.max(0, Math.floor(scroll() / itemHeight()) - props.buffer));
  const endIndex = createMemo(() => Math.min(props.fonts.length, startIndex() + visibleCount()));
  const visibleFonts = createMemo(() => props.fonts.slice(startIndex(), endIndex()));
  const totalHeight = createMemo(() => props.fonts.length * itemHeight());


  onMount(() => {
    const resizeOBS = new ResizeObserver((entries) => {
      const rect = entries[0].contentRect;
      setContainerHeight(rect.height)
    })
    resizeOBS.observe(containerREF)
    setContainerHeight(containerREF.clientHeight);
    onCleanup(() => resizeOBS.disconnect())
  })

  const reportHeight = (h) => setItemHeight(h)
  let ticking = false;
  const handleScroll = (e) => {
    const value = e.currentTarget.scrollTop;
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(() => {
        setScroll(value);
        ticking = false;
      });
    }
  };



  function FontItem(props) {
    let REF;
    let mesured = false

    onMount(() => {
      if (!mesured && props.index === 0 && REF) {
        const height = REF.getBoundingClientRect().height
        props.reportHeight(height)
        mesured = true;
      }
      const timer = setTimeout(() => void loadFont(props.font.name), 50)
      onCleanup(() => clearTimeout(timer))
    })

    return (
      <button
        ref={REF}
        className="ghost font-item"
        popoverTarget="font-modal"
        popoverTargetAction="show"
        onClick={() => props.onSelect({id: props.font.id, name: props.font.name})}
        style={{
          position: "absolute",
          top: `${props.top}px`,
          left: 0,
          right: 0,
        }}
      >
        <p>{props.font.name}</p>
        <h1
          style={{
            "font-family": `"${props.font.name}"`,
          }}
        >{props.text() || props.font.name}</h1>
      </button>
    )
  }

  return (
    <div
      className="virtual-list"
      ref={containerREF}
      onScroll={handleScroll}
      style={{ position: "relative", "overflow-y": "auto", }}
    >
      <div style={{ height: `${totalHeight()}px`, position: "relative" }}>
        <For each={visibleFonts()}>
          {(font, i) => {
            const idx = () => startIndex() + i()
            return (
              <FontItem
                index={idx()}
                font={font}
                top={idx() * itemHeight()}
                reportHeight={reportHeight}
                onSelect={props.onSelect}
                text={props.text}
              />
            )
          }}
        </For>
      </div>

    </div>
  )
}