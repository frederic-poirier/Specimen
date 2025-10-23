import { createResource, createSignal, onCleanup } from "solid-js";

async function fetchPaths() {
  const response = await fetch("/api/folders/");
  if (!response.ok) throw new Error("failed to resolve path");
  return response.json();
}

export function useDirectory() {
  const [pathStatus, setPathStatus] = createSignal({
    valid: false,
    error: "empty",
    path: "",
  });
  const [paths, { mutate }] = createResource(fetchPaths);

  let timeoutID;
  const clearValidationDebounce = () => {
    if (timeoutID) {
      clearTimeout(timeoutID);
      timeoutID = undefined;
    }
  };

  const pathAlreadyExists = (candidatePath) => {
    const currentPaths = paths() ?? [];
    return currentPaths.some((entry) => entry.path === candidatePath);
  };

  const validatePath = (candidatePath) => {
    clearValidationDebounce();

    const normalizedPath = (candidatePath ?? "").trim();

    if (normalizedPath === "") {
      setPathStatus({ valid: false, error: "empty", path: "" });
      return;
    }

    timeoutID = setTimeout(async () => {
      if (pathAlreadyExists(normalizedPath)) {
        setPathStatus({
          valid: false,
          error: "Path already saved",
          path: normalizedPath,
        });
        return;
      }

      try {
        const response = await fetch(
          `/api/folders/validate?path=${encodeURIComponent(normalizedPath)}`
        );
        if (!response.ok) throw new Error("failed to validate");
        const data = await response.json();
        setPathStatus({ ...data, path: normalizedPath });
      } catch (err) {
        console.error(err);
        setPathStatus({
          valid: false,
          error: "Validation failed",
          path: normalizedPath,
        });
      }
    }, 300);
  };

  const submitPath = async (event) => {
    event.preventDefault();
    const status = pathStatus();

    if (!status.valid || !status.path) return;

    const tempId = `temp-${crypto.randomUUID()}`;
    const optimisticItem = {
      id: tempId,
      path: status.path,
      file_count: 0,
      status: "idle",
    };

    mutate((current = []) => [...current, optimisticItem]);

    try {
      const response = await fetch(
        `/api/folders/?path=${encodeURIComponent(status.path)}`,
        {
          method: "POST",
        }
      );
      if (!response.ok) throw new Error("failed to submit the path");
      const savedItem = await response.json();

      mutate((current = []) =>
        current.map((item) => (item.id === tempId ? savedItem : item))
      );

      if (typeof event.currentTarget?.reset === "function") {
        event.currentTarget.reset();
      }
      setPathStatus({ valid: false, error: "empty", path: "" });
    } catch (err) {
      console.error(err);
      mutate((current = []) => current.filter((item) => item.id !== tempId));
    }
  };

  const delPath = async (id) => {
    const currentPaths = paths() ?? [];
    const index = currentPaths.findIndex((entry) => entry.id === id);
    if (index === -1) return;

    const removed = currentPaths[index];
    mutate((prev = []) => prev.filter((entry) => entry.id !== id));

    try {
      const response = await fetch(`/api/folders/${encodeURIComponent(id)}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error("failed to validate the removal");
    } catch (err) {
      console.error(err);
      mutate((prev = []) => {
        const next = [...prev];
        next.splice(index, 0, removed);
        return next;
      });
    }
  };

  onCleanup(clearValidationDebounce);

  return {
    path: paths,
    pathStatus,
    validatePath,
    submitPath,
    delPath,
  };
}
