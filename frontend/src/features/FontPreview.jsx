import { createResource, createSignal, createMemo, onMount, onCleanup, Show, For, createRenderEffect, from, createEffect, } from "solid-js";
import { AlertIcon, DocumentSearchIcon, LoadingIcon, RemoveIcon } from "../assets/icons";
import List from "../component/List";
import { InputField, InputRoot, InputFile, Status, useStatus } from '../component/Inputs'
import { useDirectory } from "../utils/useDirectory"
import "../styles/FontPreview.css"

const loadedFonts = new Set();

async function loadFont(url, name) {
  if (!name || loadedFonts.has(name)) return;
  if (typeof document === "undefined" || typeof FontFace === "undefined") return;
  try {
    if (document.fonts && document.fonts.check(`1em "${name}"`)) {
      loadedFonts.add(name);
    }
  } catch {
    throw new Error("pas de fetch")
  }

  const face = new FontFace(name, url);
  await face.load();
  document.fonts?.add(face);
  loadedFonts.add(name);
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

export default function FontPreview() {
  const [search, setSearch] = createSignal("");
  const [family, setFamily] = createSignal(null)
  const [text, setText] = createSignal("The fox jump over the lazy dog")
  const [familyData] = createResource(family, fetchFamily)
  const [representatives] = createResource(fetchRepresentatives);
  let time

  function handleQuery(value) {
    if (time) clearTimeout(time)
    time = setTimeout(() => setSearch(value), 300);
  }

  const filteredFonts = createMemo(() => {
    const data = representatives() ?? [];
    console.log(data)
    const term = search().trim().toLowerCase();
    if (!term) return data;
    return data.filter((font) => font.name.toLowerCase().includes(term));
  });


  function FontItem(props) {
    onMount(() => {
      const name = props.item.name
      const url = `url(/api/fonts/${name.replaceAll(" ", "-")}.woff2)`
      const timer = setTimeout(() => void loadFont(url, name), 50)
      onCleanup(() => clearTimeout(timer))
    })

    return (
      <button
        className="btn--ghost font-item"
        popoverTarget="font-modal"
        popoverTargetAction="show"
        onClick={() => setFamily({ id: props.item.id, name: props.item.name })}
      >
        <p className="font-data">
          <span className="family">{props.item.name}</span>
          <span className="format">
            <For each={props.item.extensions}>
              {(extension) => <span>{extension}</span>}
            </For>
          </span>
          <span className="counts">{props.item.font_count}</span>
        </p>
        <h1
          style={{
            "font-family": `"${props.item.name}"`,
          }}
        >{text() ? text() : props.item.name}</h1>
      </button>
    )
  }

  function FontModal() {

    createEffect(async () => {
      const fonts = familyData();
      if (!fonts?.length) return;

      (async () => {
        for (const font of fonts) {
          const url = `url(/font?path=${encodeURI(font.path)}`
          await loadFont(url, font.full_name);
        }
      })();
    })

    return (
      <section id="font-modal" popover className="modal">
        <div className="font-modal-content">
          <header>
            <h5>{family()?.name}</h5>
            <button popoverTarget="font-modal" className="btn btn--ghost">
              <RemoveIcon />
            </button>
          </header>
          <ul>
            <For each={familyData()}>
              {(font) =>
                < li >
                  <h1 style={{ "font-family": family().name }}>{font.full_name}</h1>
                </li>

              }
            </For>
          </ul>
        </div>
      </section >
    )
  }

  return (
    <section id="font-viewer">
      <Show when={!representatives.error} fallback={<ErrorPreview />}>
        <Show when={!representatives.loading} fallback={<LoadingPreview />}>
          <Show when={representatives().length !== 0} fallback={<EmptyPreview />}>
            <Show when={filteredFonts().length !== 0} fallback={<EmptySearch />}>
              <List items={filteredFonts()} buffer={6} padding={48}>
                {(item, index) => <FontItem item={item} index={index} />}
              </List>
            </Show>
            <input
              type="search"
              id="font-search"
              placeholder="Search fonts..."
              onInput={(event) => handleQuery(event.currentTarget.value)}
            />
            <FontModal />
          </Show>
        </Show>
      </Show>
    </section>
  );
}

function LoadingPreview() {
  return (
    <div className="status loading">
      <LoadingIcon />
      <h5>Chargement des polices…</h5>
      <p>Les aperçus de polices sont en cours de préparation. Cette opération peut prendre quelques secondes.</p>
    </div>
  );
}

function ErrorPreview() {
  return (
    <div className="status error">
      <AlertIcon />
      <h5>Échec du chargement des polices</h5>
      <p>Une erreur est survenue lors de la récupération des données. Vérifiez votre connexion ou réessayez plus tard.</p>
    </div>
  );
}

function EmptyPreview() {
  const { validator, postPath } = useDirectory()
  const path = useStatus(validator)

  function handleSubmit() {
    postPath(path.status().value)
  }

  return (
    <div className="status empty">
      <h5>Aucune police détectée</h5>
      <p>
        Aucune source de polices n’a encore été ajoutée. Vous pouvez :
        spécifier un dossier manuellement via le champ ci-dessous,
        glisser un dossier de polices directement dans la fenêtre,
        ou lancer une analyse automatique.
      </p>

      <form onSubmit={handleSubmit} class="directory-panel-manual">
        <InputRoot>
          <InputFile
            onInput={(e) => path.validate(e.currentTarget.value)}
          />
          <hr />
          <InputField
            type="text"
            value={path.status().value}
            onInput={(e) => path.validate(e.currentTarget.value)}
          />
          <Status status={path.status} />
        </InputRoot>
        <button
          className="btn"
          type="submit"
          disabled={!path.status().valid}
        >
          Ajouter
        </button>
      </form>

      <span className="or"><span>ou</span></span>

      <button className="btn btn--full">
        <DocumentSearchIcon />
        <span>Analyser automatiquement</span>
      </button>
    </div>
  );
}

function EmptySearch() {
  return (
    <div className="status empty">
      <h5>Aucune correspondance trouvée</h5>
      <p>
        Aucun résultat ne correspond à votre recherche. Essayez d’élargir vos critères
        ou de modifier les filtres actifs.
      </p>
    </div>
  );
}