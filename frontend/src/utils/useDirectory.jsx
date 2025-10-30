import { createResource } from "solid-js";

export function useDirectory() {
  const [paths, { mutate }] = createResource(async () => {
    const res = await fetch("/api/folders/");
    if (!res.ok) throw new Error("failed to resolve path");
    return res.json();
  });

  const pathAlreadyExists = (candidate) => {
    return (paths() ?? []).some((p) => p.path === candidate);
  };

  const validator = async (path) => {
    if (pathAlreadyExists(path)) {
      return { valid: false, error: "Path already exists" };
    }
    const res = await fetch(`/api/folders/validate?path=${encodeURIComponent(path)}`);
    if (!res.ok) return { valid: false, error: "Server error" };
    const data = await res.json();
    return { valid: data.valid, error: data.error };
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

  return { paths, validator, delPath };
}
