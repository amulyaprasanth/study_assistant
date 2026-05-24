const BASE = "studyassistant-production-a9a1.up.railway.app";

export interface MCQItem {
  question: string;
  options: string[];
  answer: string;
  explanation: string;
}

export interface FlashcardItem {
  question: string;
  answer: string;
}

export interface RevisionNotes {
  title: string;
  key_concepts: string[];
  definitions: string[];
  formulas: string[];
  exam_points: string[];
}

export async function uploadFiles(
  files: File[],
): Promise<{ message: string; docs_loaded: boolean }> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Upload failed");
  return res.json();
}

export async function resetDB(): Promise<void> {
  await fetch(`${BASE}/reset`, { method: "POST" });
}

export async function fetchSummary(): Promise<string> {
  const res = await fetch(`${BASE}/summary`);
  if (!res.ok) throw new Error((await res.json()).detail ?? "Failed");
  const data = await res.json();
  return data.summary;
}

export async function fetchQuiz(): Promise<MCQItem[]> {
  const res = await fetch(`${BASE}/quiz`);
  if (!res.ok) throw new Error((await res.json()).detail ?? "Failed");
  return res.json();
}

export async function fetchFlashcards(): Promise<FlashcardItem[]> {
  const res = await fetch(`${BASE}/flashcards`);
  if (!res.ok) throw new Error((await res.json()).detail ?? "Failed");
  return res.json();
}

export async function fetchRevision(): Promise<RevisionNotes> {
  const res = await fetch(`${BASE}/revision`);
  if (!res.ok) throw new Error((await res.json()).detail ?? "Failed");
  return res.json();
}
