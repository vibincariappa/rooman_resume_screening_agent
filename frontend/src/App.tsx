import React, { useState, useEffect, useRef } from "react";
import {
  UploadCloud,
  FileText,
  Brain,
  CheckCircle,
  AlertCircle,
  Award,
  TrendingUp,
  User,
  Clock,
  Download,
  Trash2,
  Briefcase,
  X,
  Sparkles
} from "lucide-react";

interface FailedCandidate {
  filename: string;
  error: string;
}

interface CandidateRecord {
  rank: number;
  candidate_id: string;
  candidate_name: string;
  filename: string;
  final_score: number;
  semantic_score: number;
  skills_score: number;
  experience_score: number;
  education_score: number;
  matched_skills: string[] | string;
  missing_required_skills: string[] | string;
  recommendation: string;
  explanation: string;
}

interface BatchScreeningResult {
  job_title: string;
  total_candidates: number;
  processed_candidates: number;
  failed_candidates: FailedCandidate[];
  ranked_candidates: CandidateRecord[];
  processing_time: number;
}

interface CandidateDetails extends CandidateRecord {
  summary?: string;
  strengths?: string[];
  gaps?: string[];
}

export default function App() {
  const [jdText, setJdText] = useState("");
  const [resumes, setResumes] = useState<File[]>([]);
  const [isScreening, setIsScreening] = useState(false);
  const [progressLogs, setProgressLogs] = useState<string[]>([]);
  const [screeningResult, setScreeningResult] = useState<BatchScreeningResult | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateDetails | null>(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  const progressIntervalRef = useRef<any>(null);
  const logsList = [
    "Initializing ATS screening environment...",
    "Parsing Job Description and extracting required skills list...",
    "Generating query embedding vector from Job Description...",
    "Parsing uploaded resumes (PDF/DOCX/TXT) and normalizing layout whitespace...",
    "Extracting candidates profile records (experience years, contact details)...",
    "Encoding candidate text inputs to high-dimensional embeddings...",
    "Computing semantic cosine similarity metrics against Job Description...",
    "Evaluating skills checklists and calculating weighted score breakdowns...",
    "Spawning LLM Recruiter Reasoning engine to synthesize suitability logs...",
    "Compiling and exporting sorted candidate screening result objects..."
  ];

  // Auto-load any previous results on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/results")
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("No cached results");
      })
      .then((data) => {
        setScreeningResult(data);
        if (data.ranked_candidates && data.ranked_candidates.length > 0) {
          handleSelectCandidate(data.ranked_candidates[0].candidate_id);
        }
      })
      .catch(() => {});
  }, []);

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArr = Array.from(e.target.files);
      const validFiles = filesArr.filter((file) => {
        const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
        const isValidExt = [".pdf", ".docx", ".txt", ".md"].includes(ext);
        const isValidSize = file.size <= 5 * 1024 * 1024;
        if (!isValidExt) alert(`Unsupported file type: {file.name}`);
        if (!isValidSize) alert(`File too large (> 5MB): {file.name}`);
        return isValidExt && isValidSize;
      });
      setResumes((prev) => [...prev, ...validFiles]);
    }
  };

  const handleRemoveResume = (index: number) => {
    setResumes((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleStartScreening = async () => {
    if (!jdText.trim()) {
      setErrorMessage("Please supply a Job Description first.");
      return;
    }
    if (resumes.length === 0) {
      setErrorMessage("Please upload at least one candidate resume.");
      return;
    }
    
    setErrorMessage(null);
    setIsScreening(true);
    setProgressLogs([logsList[0]]);
    
    let logIndex = 1;
    progressIntervalRef.current = setInterval(() => {
      if (logIndex < logsList.length) {
        setProgressLogs((prev) => [...prev, logsList[logIndex]]);
        logIndex++;
      }
    }, 1200);

    const formData = new FormData();
    formData.append("job_description", jdText);
    resumes.forEach((file) => {
      formData.append("resumes", file);
    });

    try {
      const response = await fetch("http://localhost:8000/api/screen/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Server failed to process the resumes.");
      }

      const data: BatchScreeningResult = await response.json();
      setScreeningResult(data);
      if (data.ranked_candidates && data.ranked_candidates.length > 0) {
        handleSelectCandidate(data.ranked_candidates[0].candidate_id);
      } else {
        setSelectedCandidate(null);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred.");
    } finally {
      setIsScreening(false);
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    }
  };

  const handleSelectCandidate = async (candidateId: string) => {
    setSelectedCandidateId(candidateId);
    setIsLoadingDetails(true);
    try {
      const response = await fetch(`http://localhost:8000/api/results/${candidateId}`);
      if (!response.ok) throw new Error("Failed to load candidate details");
      const data = await response.json();
      setSelectedCandidate(data);
    } catch (err: any) {
      console.error(err);
      const fallback = screeningResult?.ranked_candidates.find((c) => c.candidate_id === candidateId);
      if (fallback) {
        setSelectedCandidate(fallback);
      }
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const downloadJSON = () => {
    if (!screeningResult) return;
    const blob = new Blob([JSON.stringify(screeningResult, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ranked_candidates.json";
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadCSV = () => {
    if (!screeningResult) return;
    const headers = [
      "rank",
      "candidate_id",
      "candidate_name",
      "filename",
      "final_score",
      "semantic_score",
      "skills_score",
      "experience_score",
      "education_score",
      "matched_skills",
      "missing_required_skills",
      "recommendation"
    ];
    
    const rows = screeningResult.ranked_candidates.map((cand) => {
      const matched = Array.isArray(cand.matched_skills) 
        ? cand.matched_skills.join(", ") 
        : cand.matched_skills;
      const missing = Array.isArray(cand.missing_required_skills) 
        ? cand.missing_required_skills.join(", ") 
        : cand.missing_required_skills;
        
      return [
        cand.rank,
        cand.candidate_id,
        `"${cand.candidate_name.replace(/"/g, '""')}"`,
        cand.filename,
        cand.final_score,
        cand.semantic_score,
        cand.skills_score,
        cand.experience_score,
        cand.education_score,
        `"${matched.replace(/"/g, '""')}"`,
        `"${missing.replace(/"/g, '""')}"`,
        cand.recommendation
      ].join(",");
    });

    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ranked_candidates.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec?.toLowerCase()) {
      case "strong match":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "good match":
        return "bg-sky-500/10 text-sky-400 border-sky-500/20";
      case "potential match":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      default:
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-sky-400";
    if (score >= 40) return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* Top Banner Header */}
      <header className="border-b border-slate-800 bg-slate-950 px-6 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-sky-500 to-indigo-600 p-2.5 rounded-xl shadow-lg shadow-sky-500/10">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              ATS Recruiter Agent
            </h1>
            <p className="text-xs text-slate-400">Transparent AI Candidate Screening</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs text-slate-400">Deterministic Model: 30% Semantic / 45% Skills / 15% Exp / 10% Edu</span>
        </div>
      </header>

      {/* Main Layout Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Input Sidebar Panel */}
        <aside className="w-[380px] border-r border-slate-800 bg-slate-950/45 p-6 flex flex-col gap-6 overflow-y-auto shrink-0">
          {/* Job Description Block */}
          <div className="flex flex-col gap-3">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-sky-400" /> Job Description
            </label>
            <textarea
              className="w-full h-44 bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/30 transition-colors resize-none placeholder-slate-500"
              placeholder="Paste job details, duties, required qualifications, and preferred tech stack here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
          </div>

          {/* Resumes Upload Block */}
          <div className="flex flex-col gap-3">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-sky-400" /> Candidate Resumes
            </label>
            
            <div className="border border-dashed border-slate-800 rounded-lg p-4 flex flex-col items-center justify-center bg-slate-900/30 hover:bg-slate-900/55 transition-colors cursor-pointer relative group">
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={handleResumeChange}
              />
              <UploadCloud className="w-8 h-8 text-slate-500 group-hover:text-sky-400 transition-colors mb-2" />
              <span className="text-xs font-medium text-slate-300">Upload multiple files</span>
              <span className="text-[10px] text-slate-500 mt-1">PDF, DOCX, TXT, MD up to 5MB</span>
            </div>

            {/* List of uploaded files */}
            {resumes.length > 0 && (
              <div className="flex flex-col gap-2 max-h-48 overflow-y-auto mt-2 border-t border-slate-800/50 pt-2">
                {resumes.map((file, idx) => {
                  const ext = file.name.substring(file.name.lastIndexOf(".")).toUpperCase();
                  return (
                    <div key={idx} className="flex items-center justify-between bg-slate-900 border border-slate-800/80 rounded-lg px-3 py-2 text-xs">
                      <div className="flex items-center gap-2 truncate">
                        <FileText className="w-4 h-4 text-sky-400 shrink-0" />
                        <span className="truncate text-slate-200">{file.name}</span>
                        <span className="text-[9px] text-slate-500 bg-slate-800 px-1 rounded uppercase shrink-0">{ext}</span>
                      </div>
                      <button
                        onClick={() => handleRemoveResume(idx)}
                        className="text-slate-500 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Trigger Button */}
          <div className="mt-auto pt-4 border-t border-slate-800/50">
            <button
              onClick={handleStartScreening}
              disabled={isScreening || !jdText.trim() || resumes.length === 0}
              className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 text-white font-medium text-sm py-3 px-4 rounded-lg shadow-lg shadow-sky-500/10 hover:shadow-sky-500/20 disabled:shadow-none transition-all flex items-center justify-center gap-2"
            >
              {isScreening ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  Screening Pipeline...
                </>
              ) : (
                <>
                  <Brain className="w-4 h-4" />
                  Start Screening
                </>
              )}
            </button>
          </div>
        </aside>

        {/* Middle Main Content Area */}
        <main className="flex-1 flex flex-col p-8 overflow-y-auto min-w-0 bg-slate-900/10">
          {/* Error Message Box */}
          {errorMessage && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm rounded-lg p-4 flex items-start gap-3 mb-6 shrink-0">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div className="flex-1">
                <span className="font-semibold">Screening Error:</span> {errorMessage}
              </div>
              <button onClick={() => setErrorMessage(null)} className="text-rose-400/60 hover:text-rose-400">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Screening Progress Indicator Overlay */}
          {isScreening && (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center gap-6 max-w-lg mx-auto w-full my-auto shadow-2xl">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-slate-800 border-t-sky-500 rounded-full animate-spin" />
                <Brain className="w-6 h-6 text-sky-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div className="text-center">
                <h3 className="font-bold text-lg text-slate-100">Batch Processing Active</h3>
                <p className="text-xs text-slate-400 mt-1">Screening resumes via NLP similarity and scoring metrics</p>
              </div>
              <div className="w-full bg-slate-900 border border-slate-800 rounded-lg p-4 font-mono text-[10px] text-sky-400 flex flex-col gap-2 max-h-40 overflow-y-auto text-left scroll-smooth">
                {progressLogs.map((log, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-slate-600">[{idx+1}]</span>
                    <span>{log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ranked Candidates Table & Summary Header */}
          {!isScreening && screeningResult && (
            <div className="flex flex-col gap-6 flex-1 min-h-0">
              {/* Summary Stats Cards */}
              <div className="grid grid-cols-4 gap-4 shrink-0">
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
                  <div className="p-3 bg-sky-500/10 text-sky-400 rounded-lg">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Target Role</span>
                    <h4 className="font-semibold text-sm text-slate-200 truncate max-w-[150px]">{screeningResult.job_title}</h4>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
                  <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-lg">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Processed Resumes</span>
                    <h4 className="font-bold text-lg text-slate-200">{screeningResult.processed_candidates} / {screeningResult.total_candidates}</h4>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
                  <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Screening Time</span>
                    <h4 className="font-bold text-lg text-slate-200">{screeningResult.processing_time}s</h4>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
                  <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Top Match Score</span>
                    <h4 className="font-bold text-lg text-slate-200">
                      {screeningResult.ranked_candidates.length > 0 
                        ? `${screeningResult.ranked_candidates[0].final_score}%`
                        : "N/A"}
                    </h4>
                  </div>
                </div>
              </div>

              {/* Table section */}
              <div className="bg-slate-950 border border-slate-800 rounded-xl flex flex-col flex-1 min-h-0 overflow-hidden shadow-xl">
                {/* Table Toolbar Header */}
                <div className="border-b border-slate-800 px-6 py-4 flex items-center justify-between bg-slate-950 shrink-0">
                  <h3 className="font-bold text-slate-200">Ranked Candidates Catalog</h3>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={downloadJSON}
                      className="border border-slate-800 hover:bg-slate-900 text-slate-300 font-medium text-xs px-3.5 py-2 rounded-lg flex items-center gap-1.5 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" /> Export JSON
                    </button>
                    <button
                      onClick={downloadCSV}
                      className="border border-slate-800 hover:bg-slate-900 text-slate-300 font-medium text-xs px-3.5 py-2 rounded-lg flex items-center gap-1.5 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" /> Export CSV
                    </button>
                  </div>
                </div>

                {/* Main Table rows container */}
                <div className="flex-1 overflow-y-auto">
                  <table className="w-full text-left border-collapse">
                    <thead className="text-[10px] uppercase font-bold tracking-wider text-slate-500 border-b border-slate-800 bg-slate-950 sticky top-0 z-10">
                      <tr>
                        <th className="py-3.5 px-6 w-16">Rank</th>
                        <th className="py-3.5 px-6">Candidate Name</th>
                        <th className="py-3.5 px-6 w-24">Final Score</th>
                        <th className="py-3.5 px-6 w-24">Skills</th>
                        <th className="py-3.5 px-6 w-24">Semantic</th>
                        <th className="py-3.5 px-6 w-24">Experience</th>
                        <th className="py-3.5 px-6 w-44">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-sm">
                      {screeningResult.ranked_candidates.map((cand) => (
                        <tr
                          key={cand.candidate_id}
                          onClick={() => handleSelectCandidate(cand.candidate_id)}
                          className={`hover:bg-slate-900/60 cursor-pointer transition-colors ${
                            selectedCandidateId === cand.candidate_id ? "bg-sky-500/5 hover:bg-sky-500/5 border-l-2 border-l-sky-500" : ""
                          }`}
                        >
                          <td className="py-4 px-6 font-bold text-slate-400">#{cand.rank}</td>
                          <td className="py-4 px-6 font-semibold text-slate-200">
                            <div className="flex flex-col">
                              <span>{cand.candidate_name}</span>
                              <span className="text-[10px] text-slate-500 font-normal truncate max-w-[200px]">{cand.filename}</span>
                            </div>
                          </td>
                          <td className={`py-4 px-6 font-bold ${getScoreColor(cand.final_score)}`}>{cand.final_score}%</td>
                          <td className="py-4 px-6 text-slate-300">{cand.skills_score}%</td>
                          <td className="py-4 px-6 text-slate-300">{cand.semantic_score}%</td>
                          <td className="py-4 px-6 text-slate-300">{cand.experience_score}%</td>
                          <td className="py-4 px-6">
                            <span className={`inline-flex px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getRecommendationColor(cand.recommendation)}`}>
                              {cand.recommendation}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Empty State when no screening has been run yet */}
          {!isScreening && !screeningResult && (
            <div className="flex-1 border-2 border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center p-8 max-w-lg mx-auto w-full my-auto text-center bg-slate-950/20">
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl shadow-xl mb-4 text-sky-400">
                <Brain className="w-10 h-10" />
              </div>
              <h3 className="text-lg font-bold text-slate-200">Evaluate Candidates Instantly</h3>
              <p className="text-xs text-slate-500 mt-2 max-w-xs mx-auto leading-relaxed">
                Paste your target Job Description, upload PDF/DOCX resumes, and click Start Screening to calculate deterministic rankings and AI explanations.
              </p>
              <div className="flex items-center gap-4 mt-6 text-xs text-slate-400 bg-slate-900/60 px-4 py-2.5 rounded-lg border border-slate-800/80">
                <div className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> Deterministic Math</div>
                <div className="h-3 w-px bg-slate-800" />
                <div className="flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5 text-indigo-400" /> LLM Recruiter Logs</div>
              </div>
            </div>
          )}
        </main>

        {/* Right Candidate Details Sidebar Panel */}
        {screeningResult && (
          <aside className="w-[420px] border-l border-slate-800 bg-slate-950/70 overflow-y-auto shrink-0 flex flex-col">
            {selectedCandidateId && selectedCandidate ? (
              isLoadingDetails ? (
                <div className="flex flex-col items-center justify-center text-center p-8 m-auto text-slate-500">
                  <div className="w-8 h-8 border-2 border-slate-800 border-t-sky-500 rounded-full animate-spin mb-2" />
                  <span className="text-xs">Loading Candidate details...</span>
                </div>
              ) : (
                <div className="flex flex-col gap-6 p-6 flex-grow">
                  {/* Candidate header section */}
                  <div className="flex items-start justify-between border-b border-slate-800 pb-4 shrink-0">
                    <div className="min-w-0">
                      <h3 className="text-lg font-bold text-slate-200 truncate">{selectedCandidate.candidate_name}</h3>
                      <p className="text-[10px] text-slate-500 truncate mt-0.5">{selectedCandidate.filename}</p>
                      <span className={`inline-flex mt-2 px-2.5 py-0.5 rounded-full text-[9px] font-bold border uppercase tracking-wider ${getRecommendationColor(selectedCandidate.recommendation)}`}>
                        {selectedCandidate.recommendation}
                      </span>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Final Score</div>
                      <div className={`text-2xl font-black ${getScoreColor(selectedCandidate.final_score)}`}>{selectedCandidate.final_score}%</div>
                      <div className="text-[9px] text-slate-500 mt-0.5">Rank #{selectedCandidate.rank}</div>
                    </div>
                  </div>

                  {/* Score breakdown metrics list */}
                  <div className="flex flex-col gap-3">
                    <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-sky-400" /> Component Breakdown
                    </h4>
                    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col gap-3.5 text-xs">
                      {/* Skills bar */}
                      <div className="flex flex-col gap-1.5">
                        <div className="flex justify-between font-semibold">
                          <span className="text-slate-400">Skills Matching (45%)</span>
                          <span className="text-slate-200">{selectedCandidate.skills_score}%</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div className="bg-sky-500 h-full rounded-full" style={{ width: `${selectedCandidate.skills_score}%` }} />
                        </div>
                      </div>
                      {/* Semantic bar */}
                      <div className="flex flex-col gap-1.5">
                        <div className="flex justify-between font-semibold">
                          <span className="text-slate-400">Semantic Similarity (30%)</span>
                          <span className="text-slate-200">{selectedCandidate.semantic_score}%</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${selectedCandidate.semantic_score}%` }} />
                        </div>
                      </div>
                      {/* Experience bar */}
                      <div className="flex flex-col gap-1.5">
                        <div className="flex justify-between font-semibold">
                          <span className="text-slate-400">Experience Alignment (15%)</span>
                          <span className="text-slate-200">{selectedCandidate.experience_score}%</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div className="bg-amber-500 h-full rounded-full" style={{ width: `${selectedCandidate.experience_score}%` }} />
                        </div>
                      </div>
                      {/* Education bar */}
                      <div className="flex flex-col gap-1.5">
                        <div className="flex justify-between font-semibold">
                          <span className="text-slate-400">Education Check (10%)</span>
                          <span className="text-slate-200">{selectedCandidate.education_score}%</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${selectedCandidate.education_score}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Skills analysis tags */}
                  <div className="flex flex-col gap-3">
                    <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-sky-400" /> Skills Evaluation
                    </h4>
                    <div className="flex flex-col gap-2.5 text-xs">
                      {/* Matched skills */}
                      <div>
                        <div className="text-slate-500 font-semibold mb-1">Matched Required Stack:</div>
                        {Array.isArray(selectedCandidate.matched_skills) && selectedCandidate.matched_skills.length > 0 ? (
                          <div className="flex flex-wrap gap-1.5">
                            {selectedCandidate.matched_skills.map((skill, idx) => (
                              <span key={idx} className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-medium text-[10px]">
                                {skill}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-slate-500 text-xs italic">No matching skills identified.</span>
                        )}
                      </div>
                      {/* Missing skills */}
                      <div className="mt-1">
                        <div className="text-slate-500 font-semibold mb-1">Missing Required Stack:</div>
                        {Array.isArray(selectedCandidate.missing_required_skills) && selectedCandidate.missing_required_skills.length > 0 ? (
                          <div className="flex flex-wrap gap-1.5">
                            {selectedCandidate.missing_required_skills.map((skill, idx) => (
                              <span key={idx} className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded font-medium text-[10px]">
                                {skill}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-slate-500 text-xs italic">All required skills matched.</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* LLM Recruiting Reasoning summary text */}
                  <div className="flex flex-col gap-3 border-t border-slate-800/80 pt-4">
                    <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> AI Recruiter Explanations
                    </h4>
                    <div className="bg-indigo-950/20 border border-indigo-500/10 rounded-xl p-4 text-xs text-slate-300 leading-relaxed flex flex-col gap-3">
                      {selectedCandidate.summary && (
                        <div>
                          <div className="text-indigo-400 font-bold uppercase text-[9px] tracking-wider mb-0.5">Candidate Summary:</div>
                          <p>{selectedCandidate.summary}</p>
                        </div>
                      )}
                      
                      {selectedCandidate.strengths && selectedCandidate.strengths.length > 0 && (
                        <div>
                          <div className="text-emerald-400 font-bold uppercase text-[9px] tracking-wider mb-1">Candidate Strengths:</div>
                          <ul className="list-disc list-inside flex flex-col gap-1 text-[11px]">
                            {selectedCandidate.strengths.map((str, idx) => (
                              <li key={idx}>{str}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {selectedCandidate.gaps && selectedCandidate.gaps.length > 0 && (
                        <div>
                          <div className="text-rose-400 font-bold uppercase text-[9px] tracking-wider mb-1">Identified Gaps:</div>
                          <ul className="list-disc list-inside flex flex-col gap-1 text-[11px]">
                            {selectedCandidate.gaps.map((gap, idx) => (
                              <li key={idx}>{gap}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div>
                        <div className="text-indigo-400 font-bold uppercase text-[9px] tracking-wider mb-0.5">Suitability Reasoning:</div>
                        <p>{selectedCandidate.explanation}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-8 m-auto text-slate-500">
                <User className="w-10 h-10 mb-2 text-slate-600" />
                <span className="text-xs">Select a candidate from the table to inspect details</span>
              </div>
            )}
          </aside>
        )}
      </div>
    </div>
  );
}
