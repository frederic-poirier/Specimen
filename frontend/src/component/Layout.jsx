import { createSignal } from "solid-js";
import { AccountIcon, AddIcon, FolderIcon, SidebarIcon, SpecimenIcon } from "../assets/icons";
import "../styles/layout.css"

export default function Layout(props) {
    return (
        <div className="main-container">
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
        <section className="sidebar" aria-expanded={sidebarStatus()}>
            <button className="btn btn--ghost" onClick={() => setSidebarStatus(!sidebarStatus())}>
                <SidebarIcon />
            </button>
            <button className="btn btn--ghost">
                <FolderIcon />
                <Show when={sidebarStatus()}><span>Dossier</span></Show>
            </button>
            <button className="btn btn--ghost">
                <SpecimenIcon />
                <Show when={sidebarStatus()}><span>Tester</span></Show>

            </button>
            <button className="btn btn--ghost">
                <AddIcon />
                <Show when={sidebarStatus()}><span>Ajouter</span></Show>
            </button>

            <button className="btn btn--ghost end">
                <AccountIcon />
                <Show when={sidebarStatus()}><span>Freddy</span></Show>
            </button>

        </section>
    )
}