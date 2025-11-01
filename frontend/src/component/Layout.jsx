import { createSignal } from "solid-js";
import { AccountIcon, AddIcon, FolderIcon, SidebarIcon, SpecimenIcon } from "../assets/icons";

export default function Layout(props) {
    return (
        <div className="layout">
            <Sidebar />
            <main>
                <Header />
                {props.children}
            </main>
        </div>
    )
}

function Header() {
    return (
        <header>
            <nav>
                <h1>Specimen</h1>
            </nav>
        </header>
    )
}

function Sidebar() {

    const [sidebarStatus, setSidebarStatus] = createSignal(false)

    return (
        <section className="layout__sidebar" aria-expanded={sidebarStatus()}>
            <button className="u-ghost-button layout__sidebar-toggle" onClick={() => setSidebarStatus(!sidebarStatus())}>
                <SidebarIcon />
            </button>
            <button className="u-ghost-button">
                <FolderIcon />
                <Show when={sidebarStatus()}><span>Dossier</span></Show>
            </button>
            <button className="u-ghost-button">
                <SpecimenIcon />
                <Show when={sidebarStatus()}><span>Tester</span></Show>

            </button>
            <button className="u-ghost-button">
                <AddIcon />
                <Show when={sidebarStatus()}><span>Ajouter</span></Show>
            </button>

            <button className="u-ghost-button layout__sidebar-footer">
                <AccountIcon />
                <Show when={sidebarStatus()}><span>Freddy</span></Show>
            </button>

        </section>
    )
}
