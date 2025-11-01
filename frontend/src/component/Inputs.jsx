import { createSignal, onCleanup, onMount } from "solid-js";
import { FolderIcon, AlertIcon, CheckIcon, SearchIcon } from "../assets/icons";
import "../styles/inputs.css"

export function useStatus(validator) {
  const [status, setStatus] = createSignal({ value: "", valid: false, error: "empty" });

  let timeoutID;
  const clear = () => timeoutID && clearTimeout(timeoutID);
  const validate = (value) => {
    clear();
    const trimmed = (value ?? "").trim();
    setStatus({ value: trimmed, valid: false, error: "pending" });

    if (!trimmed) return setStatus({ value: "", valid: false, error: "empty" });

    timeoutID = setTimeout(async () => {
      try {
        const result = await validator(trimmed);
        setStatus({
          value: trimmed,
          valid: !!result.valid,
          error: result.error || null,
        });
      } catch {
        setStatus({ value: trimmed, valid: false, error: "Validation failed" });
      }
    }, 300);
  };

  onCleanup(clear);
  return { status, validate };
}


export function InputFile(props) {
  const name = crypto.randomUUID()
  return (
    <label
      htmlFor={name}
      className="input-file focus-subtle"
    >
      <FolderIcon />
      <input
        id={name}
        type="file"
        className="input--invisible"
        onInput={props.onInput}
      />
    </label>
  )
}

export function InputField(props) {
  return (
    <input
      type={props.type}
      placeholder={props.placeholder}
      value={props.value ?? ""}
      onInput={props.onInput}
      className="input--ghost"
    />
  )
}

export function Status(props) {
  return (
    <span className="input-status focus-subtle">
      <Show when={props.status().valid}>
        <CheckIcon />
      </Show>
      <Show when={!props.status().valid && props.status().error !== "empty"}>
        <AlertIcon tabindex={0} />
        <span className="input-error">
          {props.status().error}
        </span>
      </Show>
    </span>
  )
}

export function InputRoot(props) {
  return (
    <div className="input-container card focus-ring">
      <Show when={props.icon}>
        <span className="input-icon">
          {props.icon}
        </span>
      </Show>
      {props.children}
    </div>
  )
}