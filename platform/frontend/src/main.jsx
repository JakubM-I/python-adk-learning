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
  current_knowledge_check: null,
  completed_exercises: [],
  exercise_statuses: {},
  knowledge_check_statuses: {},
  notes: "",
  part_answers: {},
  mini_project_submission: "",
  answers: {},
  knowledge_check_answers: {},
  part_feedback: {},
  mini_project_feedback: {},
  exercise_feedback: {},
  knowledge_check_feedback: {},
};

const EXERCISE_STATUS_LABELS = {
  draft: "W trakcie",
  review: "Do sprawdzenia",
  solved: "Rozwiazane",
  needs_revision: "Do powtorki",
};

const KNOWLEDGE_CHECK_STATUS_LABELS = {
  draft: "W trakcie",
  review: "Do sprawdzenia",
  solved: "Rozwiazane",
  needs_revision: "Do powtorki",
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
  const [knowledgeCheckItems, setKnowledgeCheckItems] = useState([]);
  const [progress, setProgress] = useState(EMPTY_PROGRESS);
  const [notesDraft, setNotesDraft] = useState("");
  const [modulesError, setModulesError] = useState("");
  const [contentError, setContentError] = useState("");
  const [exercisesError, setExercisesError] = useState("");
  const [knowledgeCheckError, setKnowledgeCheckError] = useState("");
  const [progressError, setProgressError] = useState("");
  const [progressStatus, setProgressStatus] = useState("Wczytywanie postepu");
  const [reviewStatus, setReviewStatus] = useState("");
  const [reviewError, setReviewError] = useState("");
  const [isLoadingModules, setIsLoadingModules] = useState(true);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);
  const [isLoadingKnowledgeCheck, setIsLoadingKnowledgeCheck] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);

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
      if (selectedPart === "exercises" || selectedPart === "knowledge_check") {
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
    if (!selectedModuleId || selectedPart !== "knowledge_check") {
      setKnowledgeCheckError("");
      setIsLoadingKnowledgeCheck(false);
      return;
    }

    let isActive = true;

    async function loadKnowledgeCheck() {
      setIsLoadingKnowledgeCheck(true);

      try {
        const response = await fetch(`${API_BASE_URL}/api/modules/${selectedModuleId}/knowledge-check`);

        if (!response.ok) {
          throw new Error(`Backend odpowiedzial statusem ${response.status}`);
        }

        const payload = await response.json();

        if (isActive) {
          setKnowledgeCheckItems(payload.items ?? []);
          setKnowledgeCheckError("");
        }
      } catch (caughtError) {
        if (isActive) {
          setKnowledgeCheckItems([]);
          setKnowledgeCheckError(
            caughtError instanceof Error ? caughtError.message : "Nie udalo sie pobrac sprawdzenia wiedzy.",
          );
        }
      } finally {
        if (isActive) {
          setIsLoadingKnowledgeCheck(false);
        }
      }
    }

    loadKnowledgeCheck();

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
  const currentKnowledgeCheckIndex = getCurrentKnowledgeCheckIndex(
    knowledgeCheckItems,
    selectedModuleProgress.current_knowledge_check,
  );
  const currentKnowledgeCheckItem = knowledgeCheckItems[currentKnowledgeCheckIndex] ?? null;
  const currentExerciseAnswer = currentExercise ? selectedModuleProgress.answers[currentExercise.id] ?? "" : "";
  const currentKnowledgeCheckAnswer = currentKnowledgeCheckItem
    ? selectedModuleProgress.knowledge_check_answers[currentKnowledgeCheckItem.id] ?? ""
    : "";
  const currentPartAnswer = selectedModuleProgress.part_answers[selectedPart] ?? "";
  const currentMiniProjectSubmission = selectedModuleProgress.mini_project_submission ?? "";
  const currentPartFeedback = selectedModuleProgress.part_feedback[selectedPart] ?? null;
  const currentMiniProjectFeedback = selectedModuleProgress.mini_project_feedback.submission ?? null;
  const currentExerciseFeedback = currentExercise
    ? selectedModuleProgress.exercise_feedback[currentExercise.id] ?? null
    : null;
  const currentKnowledgeCheckFeedback = currentKnowledgeCheckItem
    ? selectedModuleProgress.knowledge_check_feedback[currentKnowledgeCheckItem.id] ?? null
    : null;
  const currentExerciseStatus = currentExercise
    ? selectedModuleProgress.exercise_statuses[currentExercise.id] ?? "draft"
    : "draft";
  const currentKnowledgeCheckStatus = currentKnowledgeCheckItem
    ? selectedModuleProgress.knowledge_check_statuses[currentKnowledgeCheckItem.id] ?? "draft"
    : "draft";
  const completedKnowledgeCheckCount = knowledgeCheckItems.filter(
    (item) => selectedModuleProgress.knowledge_check_statuses[item.id] === "solved",
  ).length;
  const completedAvailableParts = availableParts.filter((part) =>
    selectedModuleProgress.completed_parts.includes(part),
  );
  const progressPercent =
    availableParts.length > 0 ? Math.round((completedAvailableParts.length / availableParts.length) * 100) : 0;
  const isSelectedPartCompleted = selectedModuleProgress.completed_parts.includes(selectedPart);

  useEffect(() => {
    setNotesDraft(selectedModuleProgress.notes);
  }, [selectedModuleId, selectedModuleProgress.notes]);

  useEffect(() => {
    setReviewStatus("");
    setReviewError("");
  }, [selectedModuleId, selectedPart, currentExercise?.id, currentKnowledgeCheckItem?.id]);

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
      return payload;
    } catch (caughtError) {
      setProgressError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie zapisac postepu.");
      setProgressStatus("Blad zapisu");
      return null;
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
      return Promise.resolve(null);
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextFeedback = { ...currentModuleProgress.exercise_feedback };
      delete nextFeedback[currentExercise.id];

      return {
        ...currentModuleProgress,
        current_exercise: currentExercise.id,
        answers: {
          ...currentModuleProgress.answers,
          [currentExercise.id]: answer,
        },
        exercise_feedback: nextFeedback,
        exercise_statuses: {
          ...currentModuleProgress.exercise_statuses,
          [currentExercise.id]: "draft",
        },
      };
    });

    setProgress(nextProgress);
    return saveProgress(nextProgress);
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

  function selectKnowledgeCheckItem(index) {
    const item = knowledgeCheckItems[index];

    if (!selectedModuleId || !item) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => ({
      ...currentModuleProgress,
      current_knowledge_check: item.id,
    }));

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  function saveKnowledgeCheckAnswer(answer) {
    if (!selectedModuleId || !currentKnowledgeCheckItem) {
      return Promise.resolve(null);
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextFeedback = { ...currentModuleProgress.knowledge_check_feedback };
      delete nextFeedback[currentKnowledgeCheckItem.id];

      return {
        ...currentModuleProgress,
        current_knowledge_check: currentKnowledgeCheckItem.id,
        knowledge_check_answers: {
          ...currentModuleProgress.knowledge_check_answers,
          [currentKnowledgeCheckItem.id]: answer,
        },
        knowledge_check_feedback: nextFeedback,
        knowledge_check_statuses: {
          ...currentModuleProgress.knowledge_check_statuses,
          [currentKnowledgeCheckItem.id]: "draft",
        },
      };
    });

    setProgress(nextProgress);
    return saveProgress(nextProgress);
  }

  function savePartAnswer(partId, answer) {
    if (!selectedModuleId) {
      return Promise.resolve(null);
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextFeedback = { ...currentModuleProgress.part_feedback };
      delete nextFeedback[partId];

      return {
        ...currentModuleProgress,
        part_answers: {
          ...currentModuleProgress.part_answers,
          [partId]: answer,
        },
        part_feedback: nextFeedback,
      };
    });

    setProgress(nextProgress);
    return saveProgress(nextProgress);
  }

  function saveMiniProjectSubmission(submission) {
    if (!selectedModuleId) {
      return Promise.resolve(null);
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextFeedback = { ...currentModuleProgress.mini_project_feedback };
      delete nextFeedback.submission;

      return {
        ...currentModuleProgress,
        mini_project_submission: submission,
        mini_project_feedback: nextFeedback,
      };
    });

    setProgress(nextProgress);
    return saveProgress(nextProgress);
  }

  function setKnowledgeCheckStatus(status) {
    if (!selectedModuleId || !currentKnowledgeCheckItem) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => ({
      ...currentModuleProgress,
      current_knowledge_check: currentKnowledgeCheckItem.id,
      knowledge_check_statuses: {
        ...currentModuleProgress.knowledge_check_statuses,
        [currentKnowledgeCheckItem.id]: status,
      },
    }));

    setProgress(nextProgress);
    saveProgress(nextProgress);
  }

  async function reviewMaterial(answer) {
    if (!selectedModuleId) {
      return;
    }

    await savePartAnswer("material", answer);
    await postSegmentReview(`modules/${selectedModuleId}/review/material`);
  }

  async function reviewMiniProject(submission, answer) {
    if (!selectedModuleId) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextPartFeedback = { ...currentModuleProgress.part_feedback };
      const nextMiniProjectFeedback = { ...currentModuleProgress.mini_project_feedback };
      delete nextPartFeedback.mini_project;
      delete nextMiniProjectFeedback.submission;

      return {
        ...currentModuleProgress,
        mini_project_submission: submission,
        part_answers: {
          ...currentModuleProgress.part_answers,
          mini_project: answer,
        },
        part_feedback: nextPartFeedback,
        mini_project_feedback: nextMiniProjectFeedback,
      };
    });

    setProgress(nextProgress);
    await saveProgress(nextProgress);
    await postSegmentReview(`modules/${selectedModuleId}/review/mini-project`);
  }

  async function reviewExercises(answer) {
    if (!selectedModuleId || !currentExercise) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextFeedback = { ...currentModuleProgress.exercise_feedback };
      delete nextFeedback[currentExercise.id];

      return {
        ...currentModuleProgress,
        current_exercise: currentExercise.id,
        answers: {
          ...currentModuleProgress.answers,
          [currentExercise.id]: answer,
        },
        exercise_feedback: nextFeedback,
        exercise_statuses: {
          ...currentModuleProgress.exercise_statuses,
          [currentExercise.id]: "review",
        },
      };
    });

    setProgress(nextProgress);
    await saveProgress(nextProgress);
    await postSegmentReview(`modules/${selectedModuleId}/review/exercises`);
  }

  async function reviewKnowledgeCheck(answer) {
    if (!selectedModuleId || !currentKnowledgeCheckItem) {
      return;
    }

    const nextProgress = buildNextProgress(selectedModuleId, (currentModuleProgress) => {
      const nextFeedback = { ...currentModuleProgress.knowledge_check_feedback };
      delete nextFeedback[currentKnowledgeCheckItem.id];

      return {
        ...currentModuleProgress,
        current_knowledge_check: currentKnowledgeCheckItem.id,
        knowledge_check_answers: {
          ...currentModuleProgress.knowledge_check_answers,
          [currentKnowledgeCheckItem.id]: answer,
        },
        knowledge_check_feedback: nextFeedback,
        knowledge_check_statuses: {
          ...currentModuleProgress.knowledge_check_statuses,
          [currentKnowledgeCheckItem.id]: "review",
        },
      };
    });

    setProgress(nextProgress);
    await saveProgress(nextProgress);
    await postSegmentReview(`modules/${selectedModuleId}/review/knowledge-check`);
  }

  async function postSegmentReview(path) {
    setIsReviewing(true);
    setReviewStatus("Sprawdzam odpowiedzi...");
    setReviewError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/${path}`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error(`Backend odpowiedzial statusem ${response.status}`);
      }

      const payload = await response.json();
      setProgress(payload);
      setReviewStatus("Sprawdzone");
    } catch (caughtError) {
      setReviewError(caughtError instanceof Error ? caughtError.message : "Nie udalo sie sprawdzic odpowiedzi.");
      setReviewStatus("Blad sprawdzania");
    } finally {
      setIsReviewing(false);
    }
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
              <p className="eyebrow">Etap 6</p>
              <h2>{selectedModule?.title ?? "Wybierz modul"}</h2>
            </div>
            <span
              className={
                modulesError || contentError || exercisesError || knowledgeCheckError || progressError
                  ? "status-pill status-error"
                  : "status-pill"
              }
            >
              {modulesError || contentError || exercisesError || knowledgeCheckError || progressError
                ? "Wymaga uwagi"
                : progressStatus}
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

              <section
                className="reader-shell"
                aria-busy={isLoadingContent || isLoadingExercises || isLoadingKnowledgeCheck}
              >
                <div className="reader-header">
                  <div>
                    <p className="eyebrow">
                      {selectedPart === "exercises"
                        ? "Tryb cwiczen"
                        : selectedPart === "knowledge_check"
                          ? "Tryb sprawdzenia"
                          : "Plik Markdown"}
                    </p>
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

                {isLoadingContent || isLoadingExercises || isLoadingKnowledgeCheck ? (
                  <p className="empty-state">Wczytuje tresc modulu...</p>
                ) : null}
                {contentError ? <p className="empty-state error-text">{contentError}</p> : null}
                {exercisesError ? <p className="empty-state error-text">{exercisesError}</p> : null}
                {knowledgeCheckError ? <p className="empty-state error-text">{knowledgeCheckError}</p> : null}
                {!isLoadingContent &&
                selectedPart !== "exercises" &&
                selectedPart !== "knowledge_check" &&
                content?.markdown ? (
                  <>
                    <MarkdownReader markdown={content.markdown} />
                    {selectedPart === "material" || selectedPart === "mini_project" ? (
                      <PartWorkspacePanel
                        partId={selectedPart}
                        answer={currentPartAnswer}
                        answerFeedback={currentPartFeedback}
                        isReviewing={isReviewing}
                        miniProjectSubmission={currentMiniProjectSubmission}
                        miniProjectFeedback={currentMiniProjectFeedback}
                        onAnswerBlur={savePartAnswer}
                        onReviewMaterial={reviewMaterial}
                        onReviewMiniProject={reviewMiniProject}
                        onSubmissionBlur={saveMiniProjectSubmission}
                        reviewError={reviewError}
                        reviewStatus={reviewStatus}
                      />
                    ) : null}
                  </>
                ) : null}
                {!isLoadingExercises && selectedPart === "exercises" && currentExercise ? (
                  <ExerciseMode
                    answer={currentExerciseAnswer}
                    currentIndex={currentExerciseIndex}
                    exercise={currentExercise}
                    exerciseCount={exercises.length}
                    onAnswerBlur={saveExerciseAnswer}
                    onReview={reviewExercises}
                    onNavigate={selectExercise}
                    onStatusChange={setExerciseStatus}
                    feedback={currentExerciseFeedback}
                    isReviewing={isReviewing}
                    reviewError={reviewError}
                    reviewStatus={reviewStatus}
                    status={currentExerciseStatus}
                    statuses={selectedModuleProgress.exercise_statuses}
                    answers={selectedModuleProgress.answers}
                  />
                ) : null}
                {!isLoadingExercises && selectedPart === "exercises" && !currentExercise && !exercisesError ? (
                  <p className="empty-state">Ten modul nie ma jeszcze sparsowanych cwiczen.</p>
                ) : null}
                {!isLoadingKnowledgeCheck && selectedPart === "knowledge_check" && currentKnowledgeCheckItem ? (
                  <KnowledgeCheckMode
                    answer={currentKnowledgeCheckAnswer}
                    completedCount={completedKnowledgeCheckCount}
                    currentIndex={currentKnowledgeCheckIndex}
                    item={currentKnowledgeCheckItem}
                    itemCount={knowledgeCheckItems.length}
                    onAnswerBlur={saveKnowledgeCheckAnswer}
                    onReview={reviewKnowledgeCheck}
                    onNavigate={selectKnowledgeCheckItem}
                    onStatusChange={setKnowledgeCheckStatus}
                    feedback={currentKnowledgeCheckFeedback}
                    isReviewing={isReviewing}
                    reviewError={reviewError}
                    reviewStatus={reviewStatus}
                    status={currentKnowledgeCheckStatus}
                    statuses={selectedModuleProgress.knowledge_check_statuses}
                    answers={selectedModuleProgress.knowledge_check_answers}
                  />
                ) : null}
                {!isLoadingKnowledgeCheck &&
                selectedPart === "knowledge_check" &&
                !currentKnowledgeCheckItem &&
                !knowledgeCheckError ? (
                  <p className="empty-state">Ten modul nie ma jeszcze sparsowanych pytan sprawdzenia wiedzy.</p>
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

function PartWorkspacePanel({
  answer,
  answerFeedback,
  isReviewing,
  miniProjectSubmission,
  miniProjectFeedback,
  onAnswerBlur,
  onReviewMaterial,
  onReviewMiniProject,
  onSubmissionBlur,
  partId,
  reviewError,
  reviewStatus,
}) {
  const [answerDraft, setAnswerDraft] = useState(answer);
  const [submissionDraft, setSubmissionDraft] = useState(miniProjectSubmission);
  const isMiniProject = partId === "mini_project";

  useEffect(() => {
    setAnswerDraft(answer);
  }, [answer, partId]);

  useEffect(() => {
    setSubmissionDraft(miniProjectSubmission);
  }, [miniProjectSubmission, partId]);

  const canReviewAnswer = answerDraft.trim().length >= 4;
  const canReviewMiniProject = submissionDraft.trim().length >= 4 && canReviewAnswer;

  return (
    <section className="part-workspace" aria-label="Miejsce na odpowiedz">
      <div className="part-workspace-header">
        <div>
          <p className="eyebrow">Aktywna praca</p>
          <h4>{isMiniProject ? "Mini-projekt i pytanie sprawdzajace" : "Pytanie sprawdzajace"}</h4>
        </div>
        <span>{answerDraft.trim() || submissionDraft.trim() ? "Gotowe do zapisu" : "Puste"}</span>
      </div>

      {isMiniProject ? (
        <label className="workspace-field workspace-field-submission">
          <span>Rozwiazanie mini-projektu do sprawdzenia</span>
          <textarea
            aria-label="Rozwiazanie mini-projektu do sprawdzenia"
            onBlur={() => onSubmissionBlur(submissionDraft)}
            onChange={(event) => setSubmissionDraft(event.target.value)}
            placeholder="Wklej kod, opis decyzji albo link/sciezke do pliku z rozwiazaniem. Zapis nastapi po opuszczeniu pola."
            spellCheck="false"
            value={submissionDraft}
          />
          <ReviewFeedbackPanel feedback={miniProjectFeedback} title="Ocena rozwiazania mini-projektu" />
        </label>
      ) : null}

      <label className="workspace-field workspace-field-answer">
        <span>Odpowiedz na pytanie sprawdzajace</span>
        <textarea
          aria-label="Odpowiedz na pytanie sprawdzajace"
          onBlur={() => onAnswerBlur(partId, answerDraft)}
          onChange={(event) => setAnswerDraft(event.target.value)}
          placeholder="Zapisz swoja odpowiedz. Platforma przechowa ja lokalnie w postepie modulu."
          value={answerDraft}
        />
        <ReviewFeedbackPanel feedback={answerFeedback} title="Ocena pytania sprawdzajacego" />
      </label>

      <div className="review-actions">
        <button
          className="primary-action"
          disabled={isReviewing || (isMiniProject ? !canReviewMiniProject : !canReviewAnswer)}
          onMouseDown={(event) => event.preventDefault()}
          onClick={() =>
            isMiniProject
              ? onReviewMiniProject(submissionDraft, answerDraft)
              : onReviewMaterial(answerDraft)
          }
          type="button"
        >
          {isReviewing ? "Sprawdzam..." : "Sprawdz"}
        </button>
        {reviewStatus ? <span className="review-status-text">{reviewStatus}</span> : null}
      </div>
      {reviewError ? <p className="error-text">{reviewError}</p> : null}
    </section>
  );
}

function ExerciseMode({
  answer,
  answers,
  currentIndex,
  exercise,
  exerciseCount,
  feedback,
  isReviewing,
  onAnswerBlur,
  onNavigate,
  onReview,
  onStatusChange,
  reviewError,
  reviewStatus,
  status,
  statuses,
}) {
  const [answerDraft, setAnswerDraft] = useState(answer);

  useEffect(() => {
    setAnswerDraft(answer);
  }, [answer, exercise.id]);

  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex < exerciseCount - 1;
  const isLastExercise = currentIndex === exerciseCount - 1;

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
        <ReviewFeedbackPanel feedback={feedback} title="Ocena cwiczenia" />
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
          <button className="secondary-action" onClick={() => onStatusChange("needs_revision")} type="button">
            Do powtorki
          </button>
        </div>
        <button className="secondary-action" disabled={!canGoNext} onClick={() => onNavigate(currentIndex + 1)} type="button">
          Nastepne
        </button>
      </div>

      {isLastExercise ? (
        <SegmentReviewSummary
          answers={answers}
          isReviewing={isReviewing}
          itemCount={exerciseCount}
          itemLabel="cwiczen"
          onReview={() => onReview(answerDraft)}
          reviewError={reviewError}
          reviewStatus={reviewStatus}
          statuses={statuses}
        />
      ) : null}
    </article>
  );
}

function KnowledgeCheckMode({
  answer,
  answers,
  completedCount,
  currentIndex,
  feedback,
  isReviewing,
  item,
  itemCount,
  onAnswerBlur,
  onNavigate,
  onReview,
  onStatusChange,
  reviewError,
  reviewStatus,
  status,
  statuses,
}) {
  const [answerDraft, setAnswerDraft] = useState(answer);

  useEffect(() => {
    setAnswerDraft(answer);
  }, [answer, item.id]);

  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex < itemCount - 1;
  const isLastItem = currentIndex === itemCount - 1;

  return (
    <article className="exercise-mode knowledge-check-mode">
      <div className="exercise-toolbar">
        <div>
          <span className="exercise-counter">
            Pytanie {currentIndex + 1} / {itemCount}
          </span>
          <h4>{item.category_label}</h4>
        </div>
        <span className={`exercise-status status-${status}`}>
          {KNOWLEDGE_CHECK_STATUS_LABELS[status] ?? status}
        </span>
      </div>

      <div className="exercise-meta">
        <span>{item.category}</span>
        <span>{item.id}</span>
        <span>{completedCount} przerobione</span>
      </div>

      <section className="exercise-section knowledge-prompt">
        <p className="eyebrow">Pytanie lub scenariusz</p>
        <MarkdownReader markdown={item.prompt_markdown} />
      </section>

      <section className="answer-panel">
        <div className="answer-header">
          <div>
            <p className="eyebrow">Twoja odpowiedz</p>
            <h4>Wyjasnij wlasnymi slowami</h4>
          </div>
          <span>{answerDraft.trim() ? "Gotowe do zapisu" : "Puste"}</span>
        </div>
        <textarea
          aria-label="Odpowiedz do pytania sprawdzenia wiedzy"
          onBlur={() => onAnswerBlur(answerDraft)}
          onChange={(event) => setAnswerDraft(event.target.value)}
          placeholder="Odpowiedz tak, jakbys tlumaczyl ten temat drugiej osobie. Zapis nastapi po opuszczeniu pola."
          spellCheck="false"
          value={answerDraft}
        />
        <ReviewFeedbackPanel feedback={feedback} title="Ocena pytania" />
      </section>

      <div className="exercise-actions">
        <button className="secondary-action" disabled={!canGoPrevious} onClick={() => onNavigate(currentIndex - 1)} type="button">
          Poprzednie
        </button>
        <div className="status-actions" aria-label="Status pytania">
          <button className="secondary-action" onClick={() => onStatusChange("draft")} type="button">
            W trakcie
          </button>
          <button className="secondary-action" onClick={() => onStatusChange("review")} type="button">
            Do sprawdzenia
          </button>
          <button className="primary-action" onClick={() => onStatusChange("solved")} type="button">
            Rozwiazane
          </button>
          <button className="secondary-action" onClick={() => onStatusChange("needs_revision")} type="button">
            Do powtorki
          </button>
        </div>
        <button className="secondary-action" disabled={!canGoNext} onClick={() => onNavigate(currentIndex + 1)} type="button">
          Nastepne
        </button>
      </div>

      {isLastItem ? (
        <SegmentReviewSummary
          answers={answers}
          isReviewing={isReviewing}
          itemCount={itemCount}
          itemLabel="pytan"
          onReview={() => onReview(answerDraft)}
          reviewError={reviewError}
          reviewStatus={reviewStatus}
          statuses={statuses}
        />
      ) : null}
    </article>
  );
}

function ReviewFeedbackPanel({ feedback, title }) {
  if (!feedback) {
    return null;
  }

  return (
    <section className={`review-feedback status-${feedback.status}`}>
      <div className="review-feedback-header">
        <p className="eyebrow">{title}</p>
        <span>{EXERCISE_STATUS_LABELS[feedback.status] ?? feedback.status}</span>
      </div>
      <p>{feedback.summary}</p>
      {feedback.comments?.length ? (
        <ul>
          {feedback.comments.map((comment, index) => (
            <li key={index}>{comment}</li>
          ))}
        </ul>
      ) : null}
      {feedback.next_step ? <p className="review-next-step">{feedback.next_step}</p> : null}
    </section>
  );
}

function SegmentReviewSummary({
  answers,
  isReviewing,
  itemCount,
  itemLabel,
  onReview,
  reviewError,
  reviewStatus,
  statuses,
}) {
  const answerCount = Object.values(answers).filter((answer) => answer.trim().length > 0).length;
  const readyCount = Object.values(statuses).filter((status) => status === "review").length;
  const solvedCount = Object.values(statuses).filter((status) => status === "solved").length;
  const needsRevisionCount = Object.values(statuses).filter((status) => status === "needs_revision").length;
  const canReview = readyCount > 0;

  return (
    <section className="segment-summary">
      <div>
        <p className="eyebrow">Podsumowanie</p>
        <h4>Gotowe do sprawdzenia</h4>
      </div>
      <div className="segment-summary-grid">
        <span>{itemCount} {itemLabel}</span>
        <span>{answerCount} odpowiedzi</span>
        <span>{readyCount} do sprawdzenia</span>
        <span>{solvedCount} rozwiazane</span>
        <span>{needsRevisionCount} do powtorki</span>
      </div>
      <div className="review-actions">
        <button
          className="primary-action"
          disabled={isReviewing || !canReview}
          onMouseDown={(event) => event.preventDefault()}
          onClick={onReview}
          type="button"
        >
          {isReviewing ? "Sprawdzam..." : "Sprawdz"}
        </button>
        {reviewStatus ? <span className="review-status-text">{reviewStatus}</span> : null}
      </div>
      {!canReview ? <p className="review-note">Oznacz przynajmniej jedna odpowiedz jako Do sprawdzenia.</p> : null}
      {reviewError ? <p className="error-text">{reviewError}</p> : null}
    </section>
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

function getCurrentKnowledgeCheckIndex(items, currentItemId) {
  if (items.length === 0) {
    return -1;
  }

  const currentIndex = items.findIndex((item) => item.id === currentItemId);

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
