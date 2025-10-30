import { createSignal } from "solid-js";
import { AccountIcon, AddIcon, FolderIcon, SidebarIcon, SpecimenIcon } from "../assets/icons";

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
            <button className="ghost" onClick={() => setSidebarStatus(!sidebarStatus())}>
                <SidebarIcon />
            </button>
            <button className="ghost">
                <FolderIcon />
                <Show when={sidebarStatus()}><span>Dossier</span></Show>
            </button>
            <button className="ghost">
                <SpecimenIcon />
                <Show when={sidebarStatus()}><span>Tester</span></Show>

            </button>
            <button className="ghost">
                <AddIcon />
                <Show when={sidebarStatus()}><span>Ajouter</span></Show>
            </button>

            <button className="ghost end">
                <AccountIcon />
                <Show when={sidebarStatus()}><span>Freddy</span></Show>
            </button>

        </section>
    )
}