import { createSignal, For } from "solid-js";
import "../styles/inputs.css"

export function Tabs(props) {
  const [selected, setSelected] = createSignal(props.initial || props.tabs[0]);

  function handleSelect(tab) {
    setSelected(tab);
    props.onChange?.(tab);
  }

  return (
    <div className="tabs">
      <For each={props.tabs}>
        {(tab) => (
          <label for={tab} className="tabs__option">
            <input
              type="radio"
              name="tabs-group"
              id={tab}
              value={tab}
              checked={selected() === tab}
              onInput={(e) => handleSelect(e.currentTarget.value)}
            />
            {tab}
          </label>
        )}
      </For>
    </div>
  );
}

import { Show } from "solid-js";
import { CheckIcon, AlertIcon, FolderIcon } from "../assets/icons";

export function InputText(props) {
  return (
    <label className="input-field">
      <input
        className="u-ghost-input"
        type="text"
        value={props.status().value}
        placeholder={props.placeholder}
        onInput={(e) => props.onInput(e.target.value)}
        autoComplete="off"
      />
      <span className="input-field__status">
        <Show when={props.status().valid}>
          <CheckIcon />
        </Show>
        <Show when={!props.status().valid && props.status().error !== "empty"}>
          <button type="button" className="input-field__status-button" popoverTarget="input-error">
            <AlertIcon />
          </button>
          <span id="input-error" popover>
            {props.status().error}
          </span>
        </Show>
      </span>
    </label >
  );
}


export function InputPath(props) {
  const handleFilePick = (e) => {
    const [file] = e.target.files ?? [];
    if (!file) return props.onInput("");
    const parts = file.webkitRelativePath.split("/");
    props.onInput("/" + (parts.length > 1 ? parts[0] : ""));
  };

  return (
    <fieldset class="input-field input-field--path">
      <label className="input-field__trigger">
        <FolderIcon />
        <input
          type="file"
          className="u-sr-only"
          webkitdirectory
          onInput={handleFilePick}
        />
      </label>
      <InputText
        placeholder={props.placeholder || "/users/fonts"}
        status={props.status}
        onInput={props.onInput}
      />
    </fieldset>
  );
}
