import { createSignal, createMemo, onMount, For } from "solid-js";

export default function VirtualList(props) {
    const ITEM_HEIGHT = props.itemHeight ?? 32; // hauteur fixe d'un item
    const BUFFER = props.buffer ?? 10;          // nombre d’items en avance

    const [scrollTop, setScrollTop] = createSignal(0);
    const [containerHeight, setContainerHeight] = createSignal(0);
    let containerRef;

    const totalCount = () => props.items.length;
    const totalHeight = () => totalCount() * ITEM_HEIGHT;

    // Nombre d'items visibles dans la fenêtre
    const visibleCount = createMemo(() =>
        Math.ceil(containerHeight() / ITEM_HEIGHT) + BUFFER
    );

    // Index de départ selon le scroll
    const startIndex = createMemo(() =>
        Math.max(0, Math.floor(scrollTop() / ITEM_HEIGHT) - BUFFER)
    );

    // Index de fin selon la fenêtre
    const endIndex = createMemo(() =>
        Math.min(totalCount(), startIndex() + visibleCount())
    );

    const visibleItems = createMemo(() =>
        props.items.slice(startIndex(), endIndex())
    );

    const handleScroll = (e) => {
        setScrollTop(e.currentTarget.scrollTop);
    };

    onMount(() => {
        setContainerHeight(containerRef.clientHeight);
    });

    return (
        <div
            ref={(el) => (containerRef = el)}
            onScroll={handleScroll}
            style={{
                position: "relative",
                overflow: "auto",
                "max-height": "460px",
                border: "1px solid #ccc",
            }}
        >
            {console.log(visibleItems())}

            <div
                style={{
                    height: `${totalHeight()}px`,
                    position: "relative",
                }}
            >
                <For each={visibleItems()}>
                    {(item, i) => {
                        const index = () => startIndex() + i();
                        return (
                            <div
                                style={{
                                    position: "absolute",
                                    top: `${index() * ITEM_HEIGHT}px`,
                                    height: `${ITEM_HEIGHT}px`,
                                    left: 0,
                                    right: 0,
                                    display: "flex",
                                    "align-items": "center",
                                    padding: "0 0.5rem",
                                }}
                            >
                                <FontItem font={item} />
                            </div>
                        );
                    }}
                </For>
            </div>
        </div>
    );
}

export function FontItem(props) {
    return (
        <div style={{ "font-family": props.font.family }}>
            {props.font.family}
        </div>
    );
}
