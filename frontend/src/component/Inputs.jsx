import { createSignal, For } from "solid-js";
import "../styles/inputs.css"

export function Tabs(props) {
  const [selected, setSelected] = createSignal(props.initial || props.tabs[0]);

  function handleSelect(tab) {
    setSelected(tab);
    props.onChange?.(tab);
  }

  return (
    <div className="tab-switch">
      <For each={props.tabs}>
        {(tab) => (
          <label for={tab}>
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
