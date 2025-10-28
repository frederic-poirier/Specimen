import { createSignal, Switch, Match, Show, For } from "solid-js";
import { Tabs } from "../component/Inputs";
import { AlertIcon, CheckIcon, FolderIcon, RemoveIcon } from "../assets/icons";
import { useDirectory } from "../utils/useDirectory";
import "../styles/Directory.css";

export default function Directory() {
  const { path, pathStatus, validatePath, submitPath, delPath } = useDirectory();

  return (
    <section className="directory-panel">
          <DirectoryHeader />
          <DirectoryList path={path() ?? []} onDelete={delPath} />
          <DirectoryForm
            pathStatus={pathStatus}
            validatePath={validatePath}
            submitPath={submitPath}
          />
    </section>
  );
}

function DirectoryHeader() {
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

function DirectoryList(props) {
  return (
    <Show when={props.path.length !== 0} fallback={"Empty"}>
      <ul className="directory-panel-list">
        <For each={props.path}>
          {(path) => (
            <li id={path.id}>
              <h3>{path.path.split("\\").at(-1)}</h3>
              <button
                className="ghost"
                onClick={() => props.onDelete(path.id)}
              >
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
  const [currentTab, setCurrentTab] = createSignal("Automatic");
  const tabs = ["Automatic", "Manual"];

  const handleDirectoryPick = (event) => {
    const [file] = event.target.files ?? [];
    if (!file) return props.validatePath("");
    props.validatePath(file.webkitRelativePath);
  };

  return (
    <>
      <button popoverTarget="directory-panel-form">Add folders to watch</button>
      <section id="directory-panel-form" popover>
        <header>
          <h5>Add folder</h5>
          <button className="ghost" popoverTarget="directory-panel-form">
            <RemoveIcon />
          </button>
        </header>
        <form onSubmit={props.submitPath}>
          <Tabs tabs={tabs} onChange={setCurrentTab} />
          <div className="directory-panel-content">
            <Switch>
              <Match when={currentTab() === "Automatic"}>
                <h5>Scan for font folders automatically</h5>
                <p>
                  Let Specimen search common font locations on your machine
                  and suggest watched folders. This mockup button does not
                  run a real scan yet.
                </p>
                <button type="button">Scan for fonts</button>
              </Match>
              <Match when={currentTab() === "Manual"}>
                <h5>Manually add a folder</h5>
                <p>
                  You can directly write the path or set it with the input
                  files. It will validate the path and you'll be able to
                  save it afterwards.
                </p>
                <div className="directory-panel-manual">
                  <fieldset>
                    <label htmlFor="manual-folder-picker">
                      <FolderIcon />
                      <input
                        onInput={handleDirectoryPick}
                        type="file"
                        id="manual-folder-picker"
                        webkitdirectory
                      />
                    </label>
                    <label htmlFor="manual-path-input">
                      <input
                        type="text"
                        id="manual-path-input"
                        onInput={(e) => props.validatePath(e.target.value)}
                        placeholder="/users/fonts"
                        autoComplete="off"
                      />
                      <Show when={props.pathStatus().valid}><CheckIcon /></Show>
                      <Show when={!props.pathStatus().valid && props.pathStatus().error !== "empty"}>
                        <button type="button" className="ghost" popoverTarget="manual-path-error">
                          <AlertIcon />
                        </button>
                        <span id="manual-path-error" popover>
                          {props.pathStatus().error}
                        </span>
                      </Show>
                    </label>
                  </fieldset>
                  <button type="submit" disabled={!props.pathStatus().valid}>
                    Add
                  </button>
                </div>
              </Match>
            </Switch>
          </div>
        </form>
      </section>
    </>
  );
}

