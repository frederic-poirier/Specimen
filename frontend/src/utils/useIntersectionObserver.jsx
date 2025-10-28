// hooks/useIntersectionObserver.ts
import { onCleanup, createEffect } from "solid-js";

export function useIntersectionObserver(elAccessor, callback, options) {
  let observer;

  createEffect(() => {
    const el = elAccessor();
    if (!el) return;

    observer = new IntersectionObserver(([entry]) => {
      callback(entry.isIntersecting);
    }, options);

    observer.observe(el);

    onCleanup(() => {
      observer?.disconnect();
    });
  });
}
