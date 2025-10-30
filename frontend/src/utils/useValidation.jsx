import { createSignal, onCleanup } from "solid-js";

export function useValidation(validator) {
    const [status, setStatus] = createSignal({ value: "", valid: false, error: "empty" })
    let timeoutID;

    const clear = () => { if (timeoutID) clearTimeout(timeoutID) }
    const validate = (value) => {
        clear();
        const trimmed = (value ?? "").trim();
        setStatus({ value: trimmed, valid: false, error: "pending" });

        if (trimmed === "") return setStatus({ value: "", valid: false, error: "empty" })
        timeoutID = setTimeout(async () => {
            try {
                const result = await validator(trimmed);
                setStatus({ value: trimmed, valid: result.valid, error: result.error || "" })
            } catch (err) {
                console.error(err)
                setStatus({ value: trimmed, valid: false, error: "Validation failed" })
            }
        }, 300)
    }

    onCleanup(clear)

    return { status, validate, reset: () => ({ value: "", valid: false, error: "empty" }) }
}