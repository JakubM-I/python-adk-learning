import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isActive = true;

    async function loadHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`);

        if (!response.ok) {
          throw new Error(`Backend odpowiedzial statusem ${response.status}`);
        }

        const payload = await response.json();

        if (isActive) {
          setHealth(payload);
          setError("");
        }
      } catch (caughtError) {
        if (isActive) {
          setError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie pobrac statusu backendu.");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadHealth();

    return () => {
      isActive = false;
    };
  }, []);

  const statusLabel = useMemo(() => {
    if (isLoading) {
      return "Sprawdzam polaczenie";
    }

    if (error) {
      return "Backend niedostepny";
    }

    return "Backend polaczony";
  }, [error, isLoading]);

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="sidebar" aria-label="Nawigacja platformy">
          <div className="brand">
            <span className="brand-mark">Py</span>
            <div>
              <p className="eyebrow">Lokalna platforma</p>
              <h1>Python ADK Learning</h1>
            </div>
          </div>

          <nav className="nav-list" aria-label="Glowne widoki">
            <button className="nav-item active" type="button">Dashboard</button>
            <button className="nav-item" type="button" disabled>Moduly</button>
            <button className="nav-item" type="button" disabled>Cwiczenia</button>
            <button className="nav-item" type="button" disabled>Notatki</button>
          </nav>
        </aside>

        <section className="content-panel">
          <header className="topbar">
            <div>
              <p className="eyebrow">Etap 1</p>
              <h2>Szkielet aplikacji</h2>
            </div>
            <span className={error ? "status-pill status-error" : "status-pill"}>
              {statusLabel}
            </span>
          </header>

          <section className="overview-grid" aria-label="Status platformy">
            <article className="metric-card">
              <span className="metric-label">Backend</span>
              <strong>{error ? "Offline" : isLoading ? "..." : "Online"}</strong>
              <p>{error || "API odpowiada na /api/health."}</p>
            </article>

            <article className="metric-card">
              <span className="metric-label">Moduly w repo</span>
              <strong>{health?.module_count ?? "..."}</strong>
              <p>Liczone z katalogu modules. Pelny czytnik pojawi sie w etapie 2.</p>
            </article>

            <article className="metric-card">
              <span className="metric-label">Tryb pracy</span>
              <strong>MVP</strong>
              <p>Najpierw pionowy wycinek, potem cwiczenia i zapis postepu.</p>
            </article>
          </section>

          <section className="work-surface">
            <div className="section-heading">
              <p className="eyebrow">Nastepny krok</p>
              <h3>Czytnik modulow</h3>
            </div>
            <p>
              Ten ekran potwierdza, ze frontend komunikuje sie z backendem. W kolejnym etapie
              podmienimy dane statusowe na realna liste modulow i widok plikow Markdown.
            </p>

            <div className="check-row">
              <span className={health?.modules_dir_exists ? "check-dot ok" : "check-dot"} />
              <span>Katalog modules {health?.modules_dir_exists ? "zostal wykryty" : "nie zostal wykryty"}.</span>
            </div>
          </section>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
