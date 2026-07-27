import React, { Fragment, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const MODULE_PARTS = [
  { id: "material", label: "Material" },
  { id: "exercises", label: "Cwiczenia" },
  { id: "mini_project", label: "Mini-projekt" },
  { id: "knowledge_check", label: "Sprawdzenie wiedzy" },
  { id: "summary", label: "Podsumowanie" },
];

const EMPTY_PROGRESS = { modules: {} };
const EMPTY_MODULE_PROGRESS = {
  completed_parts: [],
  current_exercise: null,
  completed_exercises: [],
  exercise_statuses: {},
  notes: "",
  answers: {},
};

const EXERCISE_STATUS_LABELS = {
  draft: "W trakcie",
  review: "Do sprawdzenia",
  solved: "Rozwiazane",
};

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderInlineMarkdown(text) {
  const html = escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}

function slugify(value) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function MarkdownReader({ markdown }) {
  const blocks = useMemo(() => parseMarkdown(markdown), [markdown]);

  return (
    <article className="markdown-reader">
      {blocks.map((block, index) => (
        <MarkdownBlock block={block} key={`${block.type}-${index}`} />
      ))}
    </article>
  );
}

function MarkdownBlock({ block }) {
  if (block.type === "heading") {
    const HeadingTag = `h${block.level}`;

    return (
      <HeadingTag id={slugify(block.text)}>
        {renderInlineMarkdown(block.text)}
      </HeadingTag>
    );
  }

  if (block.type === "code") {
    return (
      <pre className="code-block">
        <code>{block.code}</code>
      </pre>
    );
  }

  if (block.type === "list") {
    return (
      <ul>
        {block.items.map((item, index) => (
          <li key={index}>{renderInlineMarkdown(item)}</li>
        ))}
      </ul>
    );
  }

  return (
    <p>
      {block.lines.map((line, index) => (
        <Fragment key={index}>
          {index > 0 ? <br /> : null}
          {renderInlineMarkdown(line)}
        </Fragment>
      ))}
    </p>
  );
}

function parseMarkdown(markdown) {
  const blocks = [];
  const lines = markdown.split("\n");
  let paragraph = [];
  let listItems = [];
  let codeLines = [];
  let isInCode = false;

  function flushParagraph() {
    if (paragraph.length > 0) {
      blocks.push({ type: "paragraph", lines: paragraph });
      paragraph = [];
    }
  }

  function flushList() {
    if (listItems.length > 0) {
      blocks.push({ type: "list", items: listItems });
      listItems = [];
    }
  }

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (isInCode) {
        blocks.push({ type: "code", code: codeLines.join("\n") });
        codeLines = [];
        isInCode = false;
      } else {
        flushParagraph();
        flushList();
        isInCode = true;
      }
      continue;
    }

    if (isInCode) {
      codeLines.push(line);
      continue;
    }

    if (line.trim() === "") {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);

    if (headingMatch) {
      flushParagraph();
      flushList();
      blocks.push({
        type: "heading",
        level: headingMatch[1].length,
        text: headingMatch[2].trim(),
      });
      continue;
    }

    const listMatch = line.match(/^-\s+(.*)$/);

    if (listMatch) {
      flushParagraph();
      listItems.push(listMatch[1]);
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  if (isInCode) {
    blocks.push({ type: "code", code: codeLines.join("\n") });
  }

  flushParagraph();
  flushList();

  return blocks;
}

function App() {
  const [modules, setModules] = useState([]);
  const [selectedModuleId, setSelectedModuleId] = useState("");
  const [selectedPart, setSelectedPart] = useState("material");
  const [content, setContent] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [progress, setProgress] = useState(EMPTY_PROGRESS);
  const [notesDraft, setNotesDraft] = useState("");
  const [modulesError, setModulesError] = useState("");
  const [contentError, setContentError] = useState("");
  const [exercisesError, setExercisesError] = useState("");
  const [progressError, setProgressError] = useState("");
  const [progressStatus, setProgressStatus] = useState("Wczytywanie postepu");
  const [isLoadingModules, setIsLoadingModules] = useState(true);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);

  useEffect(() => {
    let isActive = true;

    async function loadModules() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/modules`);

        if (!response.ok) {
          throw new Error(`Backend odpowiedzial statusem ${response.status}`);
        }

        const payload = await response.json();

        if (isActive) {
          setModules(payload);
          setModulesError("");
          setSelectedModuleId((currentModuleId) => currentModuleId || payload[0]?.id || "");
        }
      } catch (caughtError) {
        if (isActive) {
          setModulesError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie pobrac modulow.");
        }
      } finally {
        if (isActive) {
          setIsLoadingModules(false);
        }
      }
    }

    loadModules();

    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    let isActive = true;

    async function loadProgress() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/progress`);

        if (!response.ok) {
          throw new Error(`Backend odpowiedzial statusem ${response.status}`);
        }

        const payload = await response.json();

        if (isActive) {
          setProgress(payload);
          setProgressError("");
          setProgressStatus("Postep wczytany");
        }
      } catch (caughtError) {
        if (isActive) {
          setProgressError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie pobrac postepu.");
          setProgressStatus("Postep niedostepny");
        }
      }
    }

    loadProgress();

    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedModuleId) {
      return;
    }

    let isActive = true;

    async function loadContent() {
      if (selectedPart === "exercises") {
        setContent(null);
        setContentError("");
        setIsLoadingContent(false);
        return;
      }

      setIsLoadingContent(true);

      try {
        const response = await fetch(`${API_BASE_URL}/api/modules/${selectedModuleId}/content/${selectedPart}`);

        if (!response.ok) {
          throw new Error(`Backend odpowiedzial statusem ${response.status}`);
        }

        const payload = await response.json();

        if (isActive) {
          setContent(payload);
          setContentError("");
        }
      } catch (caughtError) {
        if (isActive) {
          setContent(null);
          setContentError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie pobrac tresci.");
        }
      } finally {
        if (isActive) {
          setIsLoadingContent(false);
        }
      }
    }

    loadContent();

    return () => {
      isActive = false;
    };
  }, [selectedModuleId, selectedPart]);

  useEffect(() => {
    if (!selectedModuleId || selectedPart !== "exercises") {
      setExercisesError("");
      setIsLoadingExercises(false);
      return;
    }

    let isActive = true;

    async function loadExercises() {
      setIsLoadingExercises(true);

      try {
        const response = await fetch(`${API_BASE_URL}/api/modules/${selectedModuleId}/exercises`);

        if (!response.ok) {
          throw new Error(`Backend odpowiedzial statusem ${response.status}`);
        }

        const payload = await response.json();

        if (isActive) {
          setExercises(payload.exercises ?? []);
          setExercisesError("");
        }
      } catch (caughtError) {
        if (isActive) {
          setExercises([]);
          setExercisesError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie pobrac cwiczen.");
        }
      } finally {
        if (isActive) {
          setIsLoadingExercises(false);
        }
      }
    }

    loadExercises();

    return () => {
      isActive = false;
    };
  }, [selectedModuleId, selectedPart]);

  const selectedModule = modules.find((module) => module.id === selectedModuleId);
  const availableParts = selectedModule?.parts ?? [];
  const partMeta = MODULE_PARTS.find((part) => part.id === selectedPart);
  const selectedModuleProgress = getModuleProgress(progress, selectedModuleId);
  const currentExerciseIndex = getCurrentExerciseIndex(exercises, selectedModuleProgress.current_exercise);
  const currentExercise = exercises[currentExerciseIndex] ?? null;
  const currentExerciseAnswer = currentExercise ? selectedModuleProgress.answers[currentExercise.id] ?? "" : "";
  const currentExerciseStatus = currentExercise
    ? selectedModuleProgress.exercise_statuses[currentExercise.id] ?? "draft"
    : "draft";
  const completedAvailableParts = availableParts.filter((part) =>
    selectedModuleProgress.completed_parts.includes(part),
  );
  const progressPercent =
    availableParts.length > 0 ? Math.round((completedAvailableParts.length / availableParts.length) * 100) : 0;
  const isSelectedPartCompleted = selectedModuleProgress.completed_parts.includes(selectedPart);

  useEffect(() => {
    setNotesDraft(selectedModuleProgress.notes);
  }, [selectedModuleId, selectedModuleProgress.notes]);

  function selectModule(moduleId) {
    setSelectedModuleId(moduleId);
    setSelectedPart("material");
  }

  async function saveProgress(nextProgress) {
    setProgressStatus("Zapisywanie...");

    try {
      const response = await fetch(`${API_BASE_URL}/api/progress`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(nextProgress),
      });

      if (!response.ok) {
        throw new Error(`Backend odpowiedzial statusem ${response.status}`);
      }

      const payload = await response.json();
      setProgress(payload);
      setProgressError("");
      setProgressStatus("Zapisano");
    } catch (caughtError) {
      setProgressError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie zapisac postepu.");
      setProgressStatus("Blad zapisu");
    }
  }

  function buildNextProgress(moduleId, updater) {
    const currentModuleProgress = getModuleProgress(progress, moduleId);
    const nextModuleProgress = updater(currentModuleProgress);

    return {
      ...progress,
      modules: {
        ...(progress.modules ?? {}),
        [moduleId]: nextModuleProgress,
      },
    };
  }

  function toggleSelectedPartCompleted() {
    if (!selectedModuleId) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const completedParts = new Set(currentModuleProgress.completed_parts);

      if (completedParts.has(selectedPart)) {
        completedParts.delete(selectedPart);
      } else {
        completedParts.add(selectedPart);
      }

      return {
        ...currentModuleProgress,
        completed_parts: Array.from(completedParts),
      };
    });

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  function saveNotes() {
    if (!selectedModuleId) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => ({
      ...currentModuleProgress,
      notes: notesDraft,
    }));

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  function selectExercise(index) {
    const exercise = exercises[index];

    if (!selectedModuleId || !exercise) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => ({
      ...currentModuleProgress,
      current_exercise: exercise.id,
    }));

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  function saveExerciseAnswer(answer) {
    if (!selectedModuleId || !currentExercise) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => ({
      ...currentModuleProgress,
      current_exercise: currentExercise.id,
      answers: {
        ...currentModuleProgress.answers,
        [currentExercise.id]: answer,
      },
      exercise_statuses: {
        ...currentModuleProgress.exercise_statuses,
        [currentExercise.id]: currentModuleProgress.exercise_statuses[currentExercise.id] ?? "draft",
      },
    }));

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  function setExerciseStatus(status) {
    if (!selectedModuleId || !currentExercise) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const completedExercises = new Set(currentModuleProgress.completed_exercises);

      if (status === "solved") {
        completedExercises.add(currentExercise.id);
      } else {
        completedExercises.delete(currentExercise.id);
      }

      return {
        ...currentModuleProgress,
        current_exercise: currentExercise.id,
        completed_exercises: Array.from(completedExercises),
        exercise_statuses: {
          ...currentModuleProgress.exercise_statuses,
          [currentExercise.id]: status,
        },
      };
    });

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="sidebar" aria-label="Lista modulow">
          <div className="brand">
            <span className="brand-mark">Py</span>
            <div>
              <p className="eyebrow">Czytnik modulow</p>
              <h1>Python ADK Learning</h1>
            </div>
          </div>

          <div className="module-list-header">
            <span className="metric-label">Postep modulu</span>
            <strong>{isLoadingModules ? "..." : `${progressPercent}%`}</strong>
          </div>

          {modulesError ? <p className="sidebar-error">{modulesError}</p> : null}

          <nav className="module-list" aria-label="Moduly">
            {modules.map((module) => (
              <button
                className={module.id === selectedModuleId ? "module-item active" : "module-item"}
                key={module.id}
                onClick={() => selectModule(module.id)}
                type="button"
              >
                <span>Modul {module.number}</span>
                <strong>{module.title}</strong>
                <small>{getModuleCompletionLabel(module, progress)}</small>
              </button>
            ))}
          </nav>
        </aside>

        <section className="content-panel">
          <header className="topbar">
            <div>
              <p className="eyebrow">Etap 4</p>
              <h2>{selectedModule?.title ?? "Wybierz modul"}</h2>
            </div>
            <span
              className={
                modulesError || contentError || exercisesError || progressError ? "status-pill status-error" : "status-pill"
              }
            >
              {modulesError || contentError || exercisesError || progressError ? "Wymaga uwagi" : progressStatus}
            </span>
          </header>

          {selectedModule ? (
            <>
              <section className="progress-panel" aria-label="Postep modulu">
                <div className="progress-copy">
                  <span className="metric-label">Ukonczone czesci</span>
                  <strong>
                    {completedAvailableParts.length} / {availableParts.length}
                  </strong>
                </div>
                <div className="progress-track" aria-hidden="true">
                  <span style={{ width: `${progressPercent}%` }} />
                </div>
              </section>

              <nav className="part-tabs" aria-label="Czesci modulu">
                {MODULE_PARTS.map((part) => (
                  <button
                    className={getPartTabClassName(part.id, selectedPart, selectedModuleProgress)}
                    disabled={!availableParts.includes(part.id)}
                    key={part.id}
                    onClick={() => setSelectedPart(part.id)}
                    type="button"
                  >
                    {part.label}
                  </button>
                ))}
              </nav>

              <section className="reader-shell" aria-busy={isLoadingContent || isLoadingExercises}>
                <div className="reader-header">
                  <div>
                    <p className="eyebrow">{selectedPart === "exercises" ? "Tryb cwiczen" : "Plik Markdown"}</p>
                    <h3>{partMeta?.label ?? selectedPart}</h3>
                  </div>
                  <div className="reader-actions">
                    <label className="complete-toggle">
                      <input
                        checked={isSelectedPartCompleted}
                        onChange={toggleSelectedPartCompleted}
                        type="checkbox"
                      />
                      <span>Ukonczona</span>
                    </label>
                    <span>{content?.filename ?? ""}</span>
                  </div>
                </div>

                {isLoadingContent || isLoadingExercises ? <p className="empty-state">Wczytuje tresc modulu...</p> : null}
                {contentError ? <p className="empty-state error-text">{contentError}</p> : null}
                {exercisesError ? <p className="empty-state error-text">{exercisesError}</p> : null}
                {!isLoadingContent && selectedPart !== "exercises" && content?.markdown ? (
                  <MarkdownReader markdown={content.markdown} />
                ) : null}
                {!isLoadingExercises && selectedPart === "exercises" && currentExercise ? (
                  <ExerciseMode
                    answer={currentExerciseAnswer}
                    currentIndex={currentExerciseIndex}
                    exercise={currentExercise}
                    exerciseCount={exercises.length}
                    onAnswerBlur={saveExerciseAnswer}
                    onNavigate={selectExercise}
                    onStatusChange={setExerciseStatus}
                    status={currentExerciseStatus}
                  />
                ) : null}
                {!isLoadingExercises && selectedPart === "exercises" && !currentExercise && !exercisesError ? (
                  <p className="empty-state">Ten modul nie ma jeszcze sparsowanych cwiczen.</p>
                ) : null}
              </section>

              <section className="notes-panel" aria-label="Prywatne notatki">
                <div className="notes-header">
                  <div>
                    <p className="eyebrow">Notatki prywatne</p>
                    <h3>Do tego modulu</h3>
                  </div>
                  <button className="secondary-action" onClick={saveNotes} type="button">
                    Zapisz notatki
                  </button>
                </div>
                <textarea
                  aria-label="Notatki do modulu"
                  onBlur={saveNotes}
                  onChange={(event) => setNotesDraft(event.target.value)}
                  placeholder="Zapisz pytania, skojarzenia albo fragmenty, do ktorych chcesz wrocic."
                  value={notesDraft}
                />
                {progressError ? <p className="error-text">{progressError}</p> : null}
              </section>
            </>
          ) : (
            <section className="reader-shell">
              <p className="empty-state">
                Nie znaleziono modulow. Dodaj folder zgodny ze schematem `modules/module-XX-short-name`.
              </p>
            </section>
          )}
        </section>
      </section>
    </main>
  );
}

function ExerciseMode({
  answer,
  currentIndex,
  exercise,
  exerciseCount,
  onAnswerBlur,
  onNavigate,
  onStatusChange,
  status,
}) {
  const [answerDraft, setAnswerDraft] = useState(answer);

  useEffect(() => {
    setAnswerDraft(answer);
  }, [answer, exercise.id]);

  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex < exerciseCount - 1;

  return (
    <article className="exercise-mode">
      <div className="exercise-toolbar">
        <div>
          <span className="exercise-counter">
            Cwiczenie {currentIndex + 1} / {exerciseCount}
          </span>
          <h4>{exercise.title}</h4>
        </div>
        <span className={`exercise-status status-${status}`}>{EXERCISE_STATUS_LABELS[status] ?? status}</span>
      </div>

      <div className="exercise-meta">
        <span>{exercise.level_label}</span>
        <span>{exercise.id}</span>
      </div>

      {exercise.goal ? (
        <section className="exercise-section">
          <p className="eyebrow">Cel</p>
          <p>{exercise.goal}</p>
        </section>
      ) : null}

      <section className="exercise-section">
        <p className="eyebrow">Opis</p>
        <MarkdownReader markdown={exercise.description_markdown} />
      </section>

      {exercise.constraints_markdown ? (
        <details className="exercise-details">
          <summary>Ograniczenia i wskazowki</summary>
          <MarkdownReader markdown={exercise.constraints_markdown} />
        </details>
      ) : null}

      <section className="answer-panel">
        <div className="answer-header">
          <div>
            <p className="eyebrow">Twoja odpowiedz</p>
            <h4>Kod, opis rozumowania albo oba</h4>
          </div>
          <span>{answerDraft.trim() ? "Gotowe do zapisu" : "Puste"}</span>
        </div>
        <textarea
          aria-label="Odpowiedz do cwiczenia"
          onBlur={() => onAnswerBlur(answerDraft)}
          onChange={(event) => setAnswerDraft(event.target.value)}
          placeholder="Wpisz rozwiazanie. Zostanie zapisane lokalnie po opuszczeniu pola."
          spellCheck="false"
          value={answerDraft}
        />
      </section>

      <details className="exercise-details expected-effect">
        <summary>Pokaz oczekiwany efekt</summary>
        <MarkdownReader markdown={exercise.expected_effect_markdown || "Brak osobnej sekcji oczekiwanego efektu."} />
      </details>

      <div className="exercise-actions">
        <button className="secondary-action" disabled={!canGoPrevious} onClick={() => onNavigate(currentIndex - 1)} type="button">
          Poprzednie
        </button>
        <div className="status-actions" aria-label="Status cwiczenia">
          <button className="secondary-action" onClick={() => onStatusChange("draft")} type="button">
            W trakcie
          </button>
          <button className="secondary-action" onClick={() => onStatusChange("review")} type="button">
            Do sprawdzenia
          </button>
          <button className="primary-action" onClick={() => onStatusChange("solved")} type="button">
            Rozwiazane
          </button>
        </div>
        <button className="secondary-action" disabled={!canGoNext} onClick={() => onNavigate(currentIndex + 1)} type="button">
          Nastepne
        </button>
      </div>
    </article>
  );
}

function getModuleProgress(progress, moduleId) {
  if (!moduleId) {
    return EMPTY_MODULE_PROGRESS;
  }

  return {
    ...EMPTY_MODULE_PROGRESS,
    ...(progress.modules?.[moduleId] ?? {}),
  };
}

function getCurrentExerciseIndex(exercises, currentExerciseId) {
  if (exercises.length === 0) {
    return -1;
  }

  const currentIndex = exercises.findIndex((exercise) => exercise.id === currentExerciseId);

  return currentIndex >= 0 ? currentIndex : 0;
}

function getModuleCompletionLabel(module, progress) {
  const moduleProgress = getModuleProgress(progress, module.id);
  const completedParts = module.parts.filter((part) => moduleProgress.completed_parts.includes(part));

  return `${completedParts.length}/${module.parts.length} czesci`;
}

function getPartTabClassName(partId, selectedPart, moduleProgress) {
  const classNames = ["part-tab"];

  if (partId === selectedPart) {
    classNames.push("active");
  }

  if (moduleProgress.completed_parts.includes(partId)) {
    classNames.push("completed");
  }

  return classNames.join(" ");
}

createRoot(document.getElementById("root")).render(<App />);
