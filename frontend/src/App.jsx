import { createResource, Show, Switch, Match } from 'solid-js';
import { Route, Navigate } from '@solidjs/router';
import Directory from './features/Directory';
import Representatives from './features/Representatives';
import "./styles/index.css";

async function fetchRepresentatives() {
  const res = await fetch('/fonts/representative', { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}

function RootRedirect() {
  const [reps] = createResource(fetchRepresentatives);
  return (
    <Switch>
      <Match when={reps.state === 'ready' && (Array.isArray(reps()) && reps().length > 0)}>
        <Navigate href="/representatives" />
      </Match>
      <Match when={reps.state === 'ready' && (!Array.isArray(reps()) || reps().length === 0)}>
        <Navigate href="/directory" />
      </Match>
      <Match when={true}>
        <main>Loading…</main>
      </Match>
    </Switch>
  );
}

function App() {
  return (
    <>
      <Route path="/" component={RootRedirect} />
      <Route path="/representatives" component={Representatives} />
      <Route path="/directory" component={Directory} />
      <Route path="*" element={<Navigate href="/" />} />
    </>
  );
}

export default App;
