import { createResource, Show, Switch, Match } from 'solid-js';
import { Route, Navigate, Router } from '@solidjs/router';
import Directory from './features/Directory';
import FontPreview from './features/FontPreview';
import Layout from './component/Layout'
import "./styles/index.css";

export default function App() {
  return (
    <Router root={Layout}>
      <Route path="/" component={FontPreview} />
      <Route path="/directory" component={Directory} />
    </Router>
  );
}

