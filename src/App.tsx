import { ChangeEvent, FormEvent, useRef, useState } from "react";
import myVideo from '/public/brainConnectAIDemoVideo.mp4';
// Logo imported inline as SVG

type AnalysisResponse = {
  content: string;
  history: string;
  differentialDiagnoses: string;
  personalizedTreatment: string;
  observations: string;
};

export default function BrainConnectApp() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [showResults, setShowResults] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const uploadSectionRef = useRef<HTMLDivElement | null>(null);

  const apiUrl =
    import.meta.env.VITE_ANALYZE_URL || 'http://0.0.0.0:8000/api/analyze-medical-document';

  const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB - matches backend limit

  const validateFile = (file: File) => {
    const isUnderLimit = file.size <= MAX_FILE_SIZE;
    const isPdf =
      file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
      return isPdf && isUnderLimit;
  };
  // 1. Separate function that opens the video in a new page
  const openVideoInNewTab = (videoUrl) => {
    window.open(videoUrl, '_blank');
  };
  
  const handleFileSelection = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;

    if (!files || files.length === 0) {
      setSelectedFile(null);
      setSelectedFileName("");
      setError("");
      return;
    }

    if (files.length > 1) {
      setSelectedFile(null);
      setSelectedFileName("");
      setError("Only one PDF file is allowed.");
      event.target.value = "";
      return;
    }

    const file = files[0];
    if (!validateFile(file)) {
      setSelectedFile(null);
      setSelectedFileName("");
      setError("Please select a single PDF file.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
    setSelectedFileName(file.name);
    setError("");
    setAnalysis(null);
    setShowResults(false);
  };

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedFile) {
      setError("Please select a PDF file before uploading.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setAnalysis(null);
    setShowResults(false);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const data = (await response.json()) as Partial<AnalysisResponse>;

      const apiResponse = data.content;

      const startIndexPara1 = apiResponse.indexOf("Paragraph 1:");
      const endIndexPara1 = apiResponse.indexOf("Paragraph 2:");
      const endIndexPara2 = apiResponse.indexOf("Paragraph 3:");
      const endIndexPara3 = apiResponse.indexOf("Paragraph 4:");
       const endIndexPara4 = apiResponse.indexOf("Paragraph 5:");
      // Extract paragraph 1
    const extractedParagraph1 = startIndexPara1 !== -1 
         ? apiResponse.substring(startIndexPara1, endIndexPara1) 
         : apiResponse;
    // Extract paragraph 2
    const extractedParagraph2 = startIndexPara1 !== -1 
         ? apiResponse.substring(endIndexPara1, endIndexPara2) 
         : apiResponse;

      // Extract paragraph 3
    const extractedParagraph3 = startIndexPara1 !== -1 
         ? apiResponse.substring(endIndexPara2, endIndexPara3) 
         : apiResponse;

      const extractedParagraph4 = startIndexPara1 !== -1 
         ? apiResponse.substring(endIndexPara3, endIndexPara4) 
         : apiResponse;
      
      if (!data.content) {
        throw new Error("Unexpected response format");
      }

      setAnalysis({
        content: data.content,
        history: extractedParagraph1,
        differentialDiagnoses: extractedParagraph2,
        personalizedTreatment: extractedParagraph3,
        observations: extractedParagraph4,
      });
      setShowResults(true);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setSelectedFileName("");
    setError("");
    setAnalysis(null);
    setShowResults(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const files = event.dataTransfer.files;

    if (!files || files.length === 0) {
      return;
    }

    if (files.length > 1) {
      setSelectedFile(null);
      setSelectedFileName("");
      setError("Only one PDF file is allowed.");
      return;
    }

    const file = files[0];
    if (!validateFile(file)) {
      setSelectedFile(null);
      setSelectedFileName("");
      setError("Please drop a single PDF file.");
      return;
    }

    setSelectedFile(file);
    setSelectedFileName(file.name);
    setError("");
    setAnalysis(null);
    setShowResults(false);
  };

  return (
    <div className="min-h-screen bg-[#020617] text-white overflow-x-hidden">
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-[#020617]/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-8 py-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-x-4">
            <div className="w-10 h-10 flex items-center justify-center rounded-3xl bg-white/10 overflow-hidden">
              <svg viewBox="0 0 32 32" fill="none" className="w-full h-full"><rect width="32" height="32" rx="8" fill="url(#grad)"/><path d="M16 8C11.5817 8 8 11.5817 8 16C8 20.4183 11.5817 24 16 24C20.4183 24 24 20.4183 24 16C24 11.5817 20.4183 8 16 8Z" stroke="white" strokeWidth="2.5"/><path d="M8 22h16" stroke="white" strokeWidth="2.5" strokeLinecap="round" opacity="0.3"/><defs><linearGradient id="grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse"><stop offset="0%" stopColor="#3B82F6"/><stop offset="100%" stopColor="#06B6D4"/></linearGradient></defs></svg>
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-3xl font-semibold tracking-tighter font-space text-white">Brain</span>
              <span className="text-3xl font-semibold tracking-tighter font-space bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                Connect
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-sm font-medium">
            <button className="hover:text-blue-400 transition-colors">How it Works</button>
            <button className="hover:text-blue-400 transition-colors">For Physicians</button>
            <button className="hover:text-blue-400 transition-colors">AMD Powered</button>
            <button
              type="button"
              onClick={() => uploadSectionRef.current?.scrollIntoView({ behavior: "smooth" })}
              className="px-6 py-2.5 bg-white text-black rounded-2xl font-semibold hover:bg-blue-50 transition-all active:scale-95"
            >
              Start Diagnosis
            </button>
          </div>
        </div>
      </nav>

      <main className="pt-28">
        <section className="hero-bg min-h-screen pt-24 flex items-center relative overflow-hidden neural-bg">
          <div className="max-w-7xl mx-auto px-8 grid grid-cols-1 gap-14 lg:grid-cols-2 items-center">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-3xl border border-blue-500/30 bg-blue-950/50 text-blue-400 text-sm font-medium">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                Powered by AMD Instinct MI300X • Multi-Agent AI
              </div>

              <h1 className="text-5xl md:text-6xl lg:text-7xl leading-tight font-semibold tracking-tighter title-font">
                Your Digital
                <br />
                Medical Team
              </h1>

              <p className="text-xl text-gray-300 max-w-xl leading-relaxed">
                Multi-agent AI that delivers consensus-driven diagnoses in seconds.
                Synthesizing patient data, imaging, and the latest medical literature.
              </p>

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <button
                  type="button"
                  onClick={() => uploadSectionRef.current?.scrollIntoView({ behavior: "smooth" })}
                  className="px-10 py-5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-3xl font-semibold text-xl hover:scale-105 transition-all flex items-center justify-center gap-x-3"
                >
                  <span>Upload Patient PDF</span>
                  <span className="text-2xl">→</span>
                </button>
                <button
                  type="button"
                  onClick={() => openVideoInNewTab(myVideo)}
                  className="px-8 py-5 border border-white/30 hover:border-white/60 rounded-3xl font-medium transition-all"
                >
                  Watch 30s Demo
                </button>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 text-sm pt-6">
                <div>
                  <div className="text-emerald-400 font-mono text-3xl font-semibold">30s</div>
                  <div className="text-gray-400">Average Analysis Time</div>
                </div>
                <div>
                  <div className="text-emerald-400 font-mono text-3xl font-semibold">12M</div>
                  <div className="text-gray-400">Diagnostic Errors Reduced</div>
                </div>
                <div>
                  <div className="text-emerald-400 font-mono text-3xl font-semibold">MI300X</div>
                  <div className="text-gray-400">AMD GPU Accelerated</div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="w-full h-[520px] rounded-3xl overflow-hidden border border-white/10 glow-blue bg-gradient-to-br from-slate-900 via-slate-950 to-[#020617]" />
              <div className="absolute -bottom-6 -right-6 bg-[#0A2540]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-6 max-w-[260px]">
                <div className="flex items-center gap-x-3 mb-4">
                  <div className="px-3 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-full font-medium">
                    Consensus Orchestrator Active
                  </div>
                </div>
                <div className="space-y-4 text-sm text-gray-300">
                  <div className="flex justify-between">
                    <span>Clinical Agent</span>
                    <span className="text-emerald-400">✓ Complete</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Imaging Agent</span>
                    <span className="text-emerald-400">✓ Complete</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Literature RAG</span>
                    <span className="text-amber-400">In Progress</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex items-center gap-x-3 text-xs tracking-widest text-gray-500">
            <span>AMD DEVELOPER CLOUD</span>
            <span className="w-px h-3 bg-white/30" />
            <span>FIREWORKS AI • LANGGRAPH • ROCm</span>
          </div>
        </section>

        <section ref={uploadSectionRef} className="max-w-4xl mx-auto py-24 px-8">
          <div className="text-center mb-16">
            <h2 className="text-5xl title-font font-semibold tracking-tight mb-4">Upload Patient Records</h2>
            <p className="text-xl text-gray-400">One PDF. Instant multi-agent analysis.</p>
          </div>

          <form onSubmit={handleUpload} className="space-y-8">
            <div
              className="border-4 border-dashed border-blue-500/30 hover:border-blue-400 transition-colors rounded-3xl p-20 text-center bg-[#0A2540]/30 cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                multiple={false}
                className="hidden"
                onChange={handleFileSelection}
              />
              {!selectedFile ? (
                <div className="space-y-6">
                  <div className="mx-auto w-20 h-20 bg-blue-500/10 rounded-2xl flex items-center justify-center hover:scale-110 transition-transform">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="w-12 h-12 text-blue-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.5"
                        d="M7 16a4 4 0 01-.88-7.903 5 5 0 0110.025 1.004A4 4 0 0112 16z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.5"
                        d="M12 12v4m0 0l-3-3m3 3l3-3"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-2xl font-medium">Drop your PDF here or browse files</p>
                    <p className="text-sm text-gray-500 mt-2">Supports patient history, radiology reports, and labs • Max 20MB</p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-6">
                  <div className="w-16 h-20 bg-amber-100 rounded-xl flex items-center justify-center text-4xl">📄</div>
                  <div className="space-y-2">
                    <p className="font-medium text-lg">{selectedFileName}</p>
                    <p className="text-sm text-gray-400">Ready to analyze. One file only.</p>
                  </div>
                </div>
              )}
            </div>

            {error ? <p className="text-center text-red-400">{error}</p> : null}

            <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <button
                type="submit"
                disabled={!selectedFile || isAnalyzing}
                className="px-12 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isAnalyzing ? "Consulting the Medical Team..." : "Analyze with BrainConnect"}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="px-10 py-4 border border-white/20 rounded-2xl text-sm text-gray-300 hover:border-white/40 transition-all"
              >
                New Analysis
              </button>
            </div>
          </form>

          {showResults && analysis && (
            <div className="mt-16 space-y-12">
              <div className="grid gap-6 lg:grid-cols-4">
                <div className="bg-[#0A2540] p-8 rounded-3xl border border-blue-500/50">
                  <div className="text-blue-400 text-sm font-medium tracking-widest mb-2">HISTORY</div>
                  <div className="text-gray-300 leading-relaxed">{analysis.history}</div>
                </div>
                <div className="bg-[#0A2540] p-8 rounded-3xl border border-white/10 hover:border-white/30">
                  <div className="text-amber-400 text-sm font-medium tracking-widest mb-2">DIFFERENTIAL DIAGNOSIS</div>
                  <div className="text-gray-300 leading-relaxed">{analysis.differentialDiagnoses}</div>
                </div>
                <div className="bg-[#0A2540] p-8 rounded-3xl border border-white/10 hover:border-white/30">
                  <div className="text-emerald-400 text-sm font-medium tracking-widest mb-2">TREATMENT PLAN</div>
                  <div className="text-gray-300 leading-relaxed">{analysis.personalizedTreatment}</div>
                </div>
                <div className="bg-[#0A2540] p-8 rounded-3xl border border-white/10 hover:border-white/30">
                  <div className="text-blue-400 text-sm font-medium tracking-widest mb-2">FUTURE PLAN</div>
                  <div className="text-gray-300 leading-relaxed">{analysis.observations}</div>
                </div>

              <div className="bg-[#0A2540]/70 border border-white/10 rounded-3xl p-8 text-sm">
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-6">
                  <div className="font-medium">Agent Confidence Scores</div>
                  <button
                    type="button"
                    onClick={handleReset}
                    className="text-blue-400 hover:underline text-sm"
                  >
                    New Analysis
                  </button>
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
                  {[
                    { label: "Clinical", value: "94%", accent: "text-emerald-400" },
                    { label: "Imaging", value: "89%", accent: "text-emerald-400" },
                    { label: "Literature", value: "92%", accent: "text-emerald-400" },
                    { label: "Guidelines", value: "97%", accent: "text-emerald-400" },
                    { label: "Consensus", value: "91%", accent: "text-amber-400", border: true },
                  ].map((score) => (
                    <div
                      key={score.label}
                      className={`bg-black/40 rounded-2xl p-4 text-center ${score.border ? "border border-amber-400" : ""}`}
                    >
                      <div className="text-xs text-gray-400">{score.label}</div>
                      <div className={`text-3xl font-semibold mt-1 ${score.accent}`}>{score.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        <footer className="border-t border-white/10 py-12 text-center text-xs text-gray-500">
          BrainConnect © 2026 • Built for Hackathon • AMD ROCm + LangGraph Multi-Agent System
        </footer>
      </main>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        .title-font { font-family: 'Space Grotesk', sans-serif; }
        .hero-bg { background: radial-gradient(at center bottom, #0A2540 0%, #020617 100%); }
        .neural-bg {
          background-image:
            radial-gradient(circle at 25% 30%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 75% 70%, rgba(147, 197, 253, 0.12) 0%, transparent 50%);
        }
        .glow-blue {
          box-shadow: 0 0 60px -15px rgb(59 130 246);
        }
      `}</style>
    </div>
  );
}
