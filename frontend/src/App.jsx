import { Route, Router } from '@solidjs/router';
import FontPreview from './features/FontPreview';
import Layout from './component/Layout'
import "./styles/index.css";

export default function App() {
  return (
    <Router root={Layout}>
      <Route path="/" component={FontPreview} />
    </Router>
  );
}

