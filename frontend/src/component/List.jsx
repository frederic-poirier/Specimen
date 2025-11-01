import { createSignal, createMemo, onCleanup, onMount, For } from "solid-js";

export default function List(props) {
    const [itemHeight, setItemHeight] = createSignal(100)
    const [containerHeight, setContainerHeight] = createSignal(100)
    const [scroll, setScroll] = createSignal(0)
    let containerREF

    const padding = props.padding ?? 0;
    const buffer = props.buffer ?? 2;


    const visibleCount = createMemo(() => Math.ceil(containerHeight() / itemHeight()) + buffer * 2);
    const startIndex = createMemo(() => Math.max(0, Math.floor((scroll() - padding) / itemHeight()) - buffer));
    const endIndex = createMemo(() => Math.min(props.items.length, startIndex() + visibleCount()));
    const visibleItems = createMemo(() => props.items.slice(startIndex(), endIndex()));
    const totalHeight = createMemo(() => props.items.length * itemHeight() + (padding * 2));

    onMount(() => {
        const resizeOBS = new ResizeObserver(([entry]) => {
            setContainerHeight(entry.contentRect.height);
            queueMicrotask(() => {
                const firstItem = containerREF.querySelector(".virtual-list__item");
                if (firstItem) {
                    const rect = firstItem.getBoundingClientRect();
                    if (rect.height > 0) setItemHeight(rect.height);
                }
            });
        });

        resizeOBS.observe(containerREF);
        setContainerHeight(containerREF.clientHeight);

        requestAnimationFrame(() => {
            const firstItem = containerREF.querySelector(".virtual-list__item");
            if (firstItem) {

                const rect = firstItem.getBoundingClientRect();
                console.log(firstItem, rect.height)

                if (rect.height > 0) setItemHeight(rect.height);
            }
        });

        onCleanup(() => resizeOBS.disconnect());
    });


    let ticking = false;
    const handleScroll = (e) => {
        const value = e.currentTarget.scrollTop;
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(() => {
                setScroll(value);
                ticking = false;
            });
        }
    };

    return (
        <div
            className="virtual-list"
            ref={containerREF}
            onScroll={handleScroll}
            style={{ position: "relative", "overflow-y": "auto", }}
        >
            <div style={{ height: `${totalHeight()}px`, position: "relative" }}>
                <For each={visibleItems()}>
                    {(item, i) => {
                        const idx = createMemo(() => startIndex() + i());
                        const top = createMemo(() => idx() * itemHeight() + padding);

                        return (
                            <div
                                class="virtual-list__item"
                                style={{
                                    position: "absolute",
                                    top: `${top()}px`,
                                    left: 0,
                                    right: 0,
                                }}
                            >
                                {props.children(item, idx())}
                            </div>
                        );
                    }}
                </For>
            </div>
        </div>
    )
}
