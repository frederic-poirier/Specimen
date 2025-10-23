import { createResource, createSignal, Switch, Match, Show, For } from "solid-js";
import { Tabs } from "./component/Inputs";
import "./Directory.css";
import { AlertIcon, CheckIcon, FolderIcon, RemoveIcon } from "./icons";

/**
 * Small presentational header with user-facing HTML text.
 *
 * Use <DirectoryHeader /> inside DirectoryInput to show a title and short
 * explanation for the folder-watching UI.
 */
export function DirectoryHeader() {
  return (
    <header aria-labelledby="directory-panel-title">
      <h1 id="directory-panel-title">Watch folders for fonts</h1>
      <p>
        Select one or more folders to watch. The application will scan these
        folders to find, analyze and display available fonts. You can add a
        folder manually (text) or choose a directory from your file system.
      </p>
    </header>
  );
}

async function getPath() {
  const response = await fetch("/api/folders/");
  if (!response.ok) throw new Error("failed to resolve path");
  return response.json();
}

export default function DirectoryInput() {
  const [path, { mutate }] = createResource(getPath);

  function delPath(ID) {
    const removed = path()[ID];
    const index = path().findIndex((path) => path.id === ID);
    mutate(path().filter((path) => path.id !== ID));

    const validateRemoval = async (ID) => {
      try {
        const response = await fetch(`api/folders/${ID}`, {
          method: "DELETE",
        });
        if (!response.ok) throw new Error("failed to validate the removal");
        return;
      } catch {
        mutate(path().splice(index, 0, removed));
        console.log("erreur deletion pas approved :(");
      }
    };

    validateRemoval(ID);
  }
  return (
    <section className="directory-panel">
      <Show when={path.loading}>Chargement</Show>
      <Show when={path.error}>erreur</Show>
      <Show when={path()}>
        <>
          <DirectoryHeader />
          <DirectoryList path={path()} />
          <DirectoryForm path={path()} mutate={mutate} />
        </>
      </Show>
    </section>
  );
}

function DirectoryList(props) {
  return (
    <Show when={props.path.length !== 0} fallback={"Empty"}>
      <ul className="directory-panel-list">
        <For each={props.path}>
          {(path) => (
            <li id={path.id}>
              <h3>{path.path.split("\\").at(-1)}</h3>
              <button onClick={() => delPath(path.id)}>
                <RemoveIcon />
              </button>
            </li>
          )}
        </For>
      </ul>
    </Show>
  )
}

function DirectoryForm(props) {
  const [pathStatus, setPathStatus] = createSignal({
    valid: false,
    error: "empty",
  });
  let timeoutID;

  function pathAlreadyExist(path) {
    const samePath = props.path.filter((p) => p.path === path);
    return samePath.length === 1;
  }

  function validatePath(path) {
    if (timeoutID) clearTimeout(timeoutID);
    if (path === "") return setPathStatus({ valid: false, error: "empty" });
    timeoutID = setTimeout(async () => {
      if (pathAlreadyExist(path))
        return setPathStatus({ valid: false, error: "Path already saved" });
      const response = await fetch(`/api/folders/validate?path=${path}`);
      if (!response.ok) throw new Error("failed to validate");
      const data = await response.json();
      setPathStatus(data);
      console.log(data);
    }, 300);
  }

  async function submitPath(e) {
    e.preventDefault();
    const tempId = `temp-${crypto.randomUUID()}`;

    const optimisticItem = {
      id: tempId,
      path: pathStatus().path,
      file_count: 0,
      status: "idle",
    };

    props.mutate([...props.path, optimisticItem]);

    try {
      const response = await fetch(`/api/folders/?path=${pathStatus().path}`, {
        method: "POST",
      });
      if (!response.ok) throw new Error("failed to submit the path");
      const savedItem = await response.json();
      props.mutate(props.path.map((item) => (item.id === tempId ? savedItem : item)));
    } catch (err) {
      props.mutate(props.path.filter((item) => item.id !== tempId));
      console.error(err);
    }
  }

  const [currentTab, setCurrentTab] = createSignal("Automatic");
  const tabs = ["Automatic", "Manual"]

  return (
    <>
      <form onSubmit={(e) => submitPath(e)} className="directory-panel-form">
        <Tabs tabs={tabs} onChange={setCurrentTab} />
        <div className="directory-panel-content">
          <Switch>
            <Match when={currentTab() === "Automatic"}>
              <h5>Scan for font folders automatically</h5>
              <p>Let Specimen search common font locations on your machine and suggest watched folders. This mockup button does not run a real scan yet.</p>
              <button type="button" aria-label="Scan for fonts">Scan for fonts</button>
            </Match>
            <Match when={currentTab() === "Manual"}>
              <h5>Manually add a folder</h5>
              <p>You can directly write the path or set it with the input files. It will validate the path and you'll be able to save it afterwards.</p>
              <div className="directory-panel-manual">
                <fieldset>
                  <label htmlFor="manual-folder-picker">
                    <FolderIcon />
                    <input
                      onInput={(e) => validatePath(e.target.files[0].webkitRelativePath, true)}
                      type="file"
                      id="manual-folder-picker"
                      webkitdirectory
                    />
                  </label>
                  <label htmlFor="manual-path-input">
                    <input
                      type="text"
                      id="manual-path-input"
                      onInput={(e) => validatePath(e.target.value)}
                      placeholder="/users/fonts"
                      autoComplete="off"
                    />
                    <span>
                      <Show when={pathStatus().valid}><CheckIcon /></Show>
                      <Show when={!pathStatus().valid && pathStatus().error !== "empty"}>
                        <button type="button" popoverTarget="manual-path-error">
                          <AlertIcon />
                        </button>
                        <span id="manual-path-error" popover>
                          {pathStatus().error}
                        </span>
                      </Show>
                    </span>
                  </label>
                </fieldset>
                <button type="submit" disabled={!pathStatus().valid}>
                  Submit
                </button>
              </div>
            </Match>
          </Switch>
        </div>
      </form>
    </>
  );
}

// getPath()
// delPath(ID)
// addPath(path)
// modPath(ID, path)
// TABLE id, file count, last watch, path
