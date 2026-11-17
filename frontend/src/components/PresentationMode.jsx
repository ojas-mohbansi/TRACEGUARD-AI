import React, { useState, useEffect, useRef } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Minimize2,
  X,
  Monitor,
  User,
  FileText,
  HelpCircle,
  BookOpen,
  Sparkles,
  Clock,
  Layers,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Copy,
  Check,
  Volume2
} from 'lucide-react';
import manifestData from '../data/presentationManifest.json';

// Presenter Color Themes for visual clarity
const PRESENTER_THEMES = {
  P1: {
    badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    ring: 'ring-amber-500/50',
    border: 'border-amber-500/60',
    dot: 'bg-amber-400',
    accent: 'text-amber-400',
  },
  P2: {
    badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    ring: 'ring-emerald-500/50',
    border: 'border-emerald-500/60',
    dot: 'bg-emerald-400',
    accent: 'text-emerald-400',
  },
  P3: {
    badge: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
    ring: 'ring-blue-500/50',
    border: 'border-blue-500/60',
    dot: 'bg-blue-400',
    accent: 'text-blue-400',
  },
  P4: {
    badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
    ring: 'ring-purple-500/50',
    border: 'border-purple-500/60',
    dot: 'bg-purple-400',
    accent: 'text-purple-400',
  },
  P5: {
    badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    ring: 'ring-rose-500/50',
    border: 'border-rose-500/60',
    dot: 'bg-rose-400',
    accent: 'text-rose-400',
  },
};

export function PresentationMode({ onClose }) {
  const slides = manifestData?.slides || [];
  const totalSlides = slides.length || 22;

  const presentersList = manifestData?.presenters ? Object.values(manifestData.presenters) : [
    { id: 'P1', name: 'Tanmay', startSlide: 1, endSlide: 4, topic: 'Project Overview & Research Scope' },
    { id: 'P2', name: 'Karthik Sai', startSlide: 5, endSlide: 9, topic: 'Chomsky Hierarchy & 5-Tuple Spec' },
    { id: 'P3', name: 'Ojas Mohbansi', startSlide: 10, endSlide: 14, topic: '13-Symbol Alphabet & Trace Proofs' },
    { id: 'P4', name: 'Darpan Jain', startSlide: 15, endSlide: 18, topic: 'Three-Way Classification & ML Engine' },
    { id: 'P5', name: 'Panda', startSlide: 19, endSlide: 22, topic: 'Consensus Scoring & Q.E.D. Defense' },
  ];

  const [currentIdx, setCurrentIdx] = useState(0);
  const [viewMode, setViewMode] = useState('presenter'); // 'presenter' | 'audience'
  const [presenterTab, setPresenterTab] = useState('script'); // 'script' | 'notes' | 'qa' | 'points'
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showThumbnails, setShowThumbnails] = useState(true);
  const [expandedQA, setExpandedQA] = useState({});
  const [copiedScript, setCopiedScript] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const containerRef = useRef(null);
  const thumbnailStripRef = useRef(null);
  const activeThumbnailRef = useRef(null);

  const currentSlide = slides[currentIdx] || {
    slideNumber: currentIdx + 1,
    title: `Slide ${currentIdx + 1}`,
    category: 'THEORY OF COMPUTATION',
    presenter: { id: 'P1', name: 'Presenter 1', role: 'Speaker', topic: 'Overview', allocatedDuration: '2.5 mins' },
    speakerNotes: '',
    spokenScript: '',
    defenseQuestions: [],
    image: `/slides/slide_${String(currentIdx + 1).padStart(2, '0')}.png`,
    keyPoints: [],
  };

  const presenterId = currentSlide.presenter?.id || 'P1';
  const theme = PRESENTER_THEMES[presenterId] || PRESENTER_THEMES.P1;

  // Sync active thumbnail into view
  useEffect(() => {
    if (activeThumbnailRef.current && thumbnailStripRef.current) {
      activeThumbnailRef.current.scrollIntoView({
        behavior: 'smooth',
        inline: 'center',
        block: 'nearest',
      });
    }
    setImageLoaded(false);
  }, [currentIdx]);

  // Fullscreen event listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Navigation handlers
  const handleNext = () => {
    if (currentIdx < totalSlides - 1) {
      setCurrentIdx((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx((prev) => prev - 1);
    }
  };

  const handleFirst = () => setCurrentIdx(0);
  const handleLast = () => setCurrentIdx(totalSlides - 1);

  const toggleFullscreen = async () => {
    try {
      if (!document.fullscreenElement) {
        if (containerRef.current) {
          await containerRef.current.requestFullscreen();
        }
      } else {
        await document.exitFullscreen();
      }
    } catch (err) {
      console.warn('Fullscreen request failed:', err);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignore if user is inside an input or editable element
      if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

      switch (e.key) {
        case 'ArrowRight':
        case 'PageDown':
        case ' ': // Spacebar
          e.preventDefault();
          handleNext();
          break;
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault();
          handlePrev();
          break;
        case 'Home':
          e.preventDefault();
          handleFirst();
          break;
        case 'End':
          e.preventDefault();
          handleLast();
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 'p':
        case 'P':
        case 'v':
        case 'V':
          e.preventDefault();
          setViewMode((prev) => (prev === 'presenter' ? 'audience' : 'presenter'));
          break;
        case 't':
        case 'T':
          e.preventDefault();
          setShowThumbnails((prev) => !prev);
          break;
        case 'Escape':
          // If in fullscreen, exit fullscreen. If not in fullscreen, close modal.
          if (document.fullscreenElement) {
            document.exitFullscreen().catch(() => {});
          } else if (onClose) {
            onClose();
          }
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIdx, totalSlides, onClose]);

  // Copy script to clipboard
  const handleCopyScript = () => {
    if (!currentSlide.spokenScript) return;
    navigator.clipboard.writeText(currentSlide.spokenScript);
    setCopiedScript(true);
    setTimeout(() => setCopiedScript(false), 2000);
  };

  // Toggle QA item expansion
  const toggleQA = (idx) => {
    setExpandedQA((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 flex flex-col bg-[#07090e] text-[#f8fafc] select-none font-sans overflow-hidden"
      role="dialog"
      aria-modal="true"
      aria-label="TraceGuard AI TOC Defense Presentation Mode"
    >
      {/* ── TOP HEADER / TOOLBAR ────────────────────────────────────── */}
      <header className="h-14 px-4 sm:px-6 border-b border-white/10 flex items-center justify-between bg-[#0e131f]/95 backdrop-blur-md z-20 shrink-0">
        {/* Left: Branding & Slide Index */}
        <div className="flex items-center space-x-3 truncate">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider bg-emerald-500/20 border border-emerald-500/40 text-emerald-400">
              TOC DEFENSE
            </span>
            <span className="hidden sm:inline-block text-xs font-semibold text-slate-300 truncate max-w-xs md:max-w-md">
              TraceGuard AI Presentation
            </span>
          </div>

          <span className="text-white/20">|</span>

          <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
            <span className="font-semibold text-white">Slide {currentIdx + 1}</span>
            <span>/</span>
            <span>{totalSlides}</span>
          </div>
        </div>

        {/* Center: Current Presenter Pill (Visible on md+ screens) */}
        <div className="hidden lg:flex items-center space-x-2.5 px-3 py-1 rounded-full bg-[#141b2b] border border-white/10">
          <span className={`w-2 h-2 rounded-full ${theme.dot} animate-pulse`} />
          <span className={`text-[11px] font-mono font-bold ${theme.accent}`}>
            {currentSlide.presenter?.id}: {currentSlide.presenter?.name}
          </span>
          <span className="text-white/20 text-xs">·</span>
          <span className="text-[11px] text-slate-300 max-w-[200px] truncate">
            {currentSlide.presenter?.topic}
          </span>
          <span className="text-white/20 text-xs">·</span>
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-400" />
            {currentSlide.presenter?.allocatedDuration || '2.5m'}
          </span>
        </div>

        {/* Right: View Toggles & Actions */}
        <div className="flex items-center space-x-2">
          {/* View Mode Toggle Pill */}
          <div className="flex items-center p-0.5 rounded-lg bg-[#141b2b] border border-white/10 text-xs font-mono">
            <button
              onClick={() => setViewMode('audience')}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md transition ${
                viewMode === 'audience'
                  ? 'bg-blue-600 text-white font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Audience View: Fullscreen Slide Display (Shortcut: P or V)"
              aria-label="Audience View"
            >
              <Monitor className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Audience</span>
            </button>
            <button
              onClick={() => setViewMode('presenter')}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md transition ${
                viewMode === 'presenter'
                  ? 'bg-emerald-600 text-white font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Presenter View: Slide with Spoken Script & Defense Q&A (Shortcut: P or V)"
              aria-label="Presenter View"
            >
              <User className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Presenter</span>
            </button>
          </div>

          {/* Toggle Thumbnails */}
          <button
            onClick={() => setShowThumbnails((prev) => !prev)}
            className={`p-2 rounded-lg border transition ${
              showThumbnails
                ? 'bg-[#141b2b] border-white/20 text-emerald-400'
                : 'bg-[#0e131f] border-white/10 text-slate-400 hover:text-white'
            }`}
            title="Toggle Thumbnail Strip (Shortcut: T)"
            aria-label="Toggle Thumbnails"
          >
            <Layers className="w-4 h-4" />
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-lg bg-[#141b2b] border border-white/10 text-slate-400 hover:text-white hover:border-white/20 transition"
            title={isFullscreen ? 'Exit Fullscreen (F)' : 'Enter Fullscreen (F)'}
            aria-label="Toggle Fullscreen"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          {/* Close Presentation Mode */}
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 transition"
            title="Close Presentation Mode (Esc)"
            aria-label="Close Presentation"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* ── PRESENTATION PROGRESS LINE ──────────────────────────────── */}
      <div className="w-full h-1 bg-[#141b2b]">
        <div
          className="h-full bg-gradient-to-r from-blue-500 via-emerald-400 to-emerald-500 transition-all duration-300"
          style={{ width: `${((currentIdx + 1) / totalSlides) * 100}%` }}
        />
      </div>

      {/* ── MAIN WORKSPACE / SLIDE STAGE ────────────────────────────── */}
      <main className="flex-1 min-h-0 flex overflow-hidden">
        {/* SLIDE CANVAS (Center Stage) */}
        <div
          className={`flex-1 flex flex-col items-center justify-center p-3 sm:p-6 transition-all duration-300 relative ${
            viewMode === 'presenter' ? 'lg:pr-3' : ''
          }`}
        >
          {/* 16:9 Slide Screen Container */}
          <div className="relative w-full h-full max-h-full flex items-center justify-center">
            <div className="relative w-full max-w-6xl aspect-[16/9] max-h-full flex items-center justify-center rounded-xl overflow-hidden bg-black/60 border border-white/10 shadow-2xl">
              {/* Image Loading Placeholder Skeleton */}
              {!imageLoaded && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0d1117] text-slate-500 space-y-3">
                  <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                  <span className="text-xs font-mono">Loading Slide {currentIdx + 1}...</span>
                </div>
              )}

              {/* Render High-Resolution Slide Image */}
              <img
                src={currentSlide.image || currentSlide.imageAsset || `/slides/slide_${String(currentIdx + 1).padStart(2, '0')}.png`}
                alt={currentSlide.title || `Slide ${currentIdx + 1}`}
                onLoad={() => setImageLoaded(true)}
                className={`w-full h-full object-contain select-none transition-opacity duration-300 ${
                  imageLoaded ? 'opacity-100' : 'opacity-0'
                }`}
              />

              {/* Floating Slide Floating Navigation Overlays (Hover) */}
              <button
                onClick={handlePrev}
                disabled={currentIdx === 0}
                className="absolute left-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-black/60 hover:bg-black/85 text-white/70 hover:text-white border border-white/10 hover:border-white/30 backdrop-blur-md opacity-0 hover:opacity-100 focus:opacity-100 transition-all disabled:opacity-0 disabled:pointer-events-none"
                aria-label="Previous Slide"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              <button
                onClick={handleNext}
                disabled={currentIdx === totalSlides - 1}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-black/60 hover:bg-black/85 text-white/70 hover:text-white border border-white/10 hover:border-white/30 backdrop-blur-md opacity-0 hover:opacity-100 focus:opacity-100 transition-all disabled:opacity-0 disabled:pointer-events-none"
                aria-label="Next Slide"
              >
                <ChevronRight className="w-5 h-5" />
              </button>

              {/* Bottom Quick Indicator Pill */}
              <div className="absolute bottom-3 left-4 px-2.5 py-1 rounded bg-black/70 backdrop-blur-md border border-white/10 text-[10px] font-mono text-slate-300 opacity-60 hover:opacity-100 transition-opacity">
                {currentSlide.category}
              </div>
            </div>
          </div>
        </div>

        {/* PRESENTER DRAWER / SIDEBAR (Presenter View Only) */}
        {viewMode === 'presenter' && (
          <aside className="w-full lg:w-[460px] xl:w-[500px] shrink-0 border-l border-white/10 bg-[#0e131f] flex flex-col z-10 transition-all duration-300 overflow-hidden">
            {/* Presenter Metadata Card */}
            <div className="p-4 border-b border-white/10 bg-[#141b2b]/60">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-sm border ${theme.badge}`}
                  >
                    {presenterId}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white leading-tight">
                      {currentSlide.presenter?.name}
                    </h3>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      {currentSlide.presenter?.role}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-slate-300">
                    <Clock className="w-3 h-3 mr-1 text-slate-400" />
                    {currentSlide.presenter?.allocatedDuration}
                  </span>
                </div>
              </div>

              <div className="mt-2.5 pt-2 border-t border-white/5 flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400 text-[11px] truncate max-w-[280px]">
                  Topic: <span className="text-white font-medium">{currentSlide.presenter?.topic}</span>
                </span>
                <span className={`text-[10px] font-bold ${theme.accent}`}>
                  Slide {currentSlide.slideNumber} of {totalSlides}
                </span>
              </div>
            </div>

            {/* Quick Presenter Jump Selector */}
            <div className="px-3 py-2 bg-[#090d15] border-b border-white/10 flex items-center space-x-1.5 overflow-x-auto text-xs font-mono shrink-0">
              <span className="text-[10px] text-slate-400 uppercase font-semibold shrink-0 mr-1">Roster:</span>
              {presentersList.map((p) => {
                const isActivePresenter = (currentSlide.presenterId === p.id) || (currentSlide.presenter?.id === p.id);
                const pTheme = PRESENTER_THEMES[p.id] || PRESENTER_THEMES.P1;
                return (
                  <button
                    key={p.id}
                    onClick={() => setCurrentIdx(p.startSlide - 1)}
                    className={`px-2 py-1 rounded-md text-[10px] whitespace-nowrap transition flex items-center gap-1.5 border ${
                      isActivePresenter
                        ? `${pTheme.badge} font-bold ring-1 ${pTheme.ring} shadow-xs`
                        : 'bg-[#141b2b] text-slate-400 hover:text-white border-white/10 hover:border-white/20'
                    }`}
                    title={`Jump to ${p.name} (Slides ${p.startSlide}–${p.endSlide})`}
                    aria-label={`Jump to ${p.name}`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${pTheme.dot}`} />
                    <span>{p.name.split(' ')[0]}</span>
                    <span className="text-[9px] opacity-70">({p.startSlide}–{p.endSlide})</span>
                  </button>
                );
              })}
            </div>

            {/* Presenter Tab Navigation */}
            <div className="flex items-center border-b border-white/10 bg-[#0b0e17] px-2 pt-1 text-xs font-mono">
              <button
                onClick={() => setPresenterTab('script')}
                className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition ${
                  presenterTab === 'script'
                    ? 'border-emerald-400 text-emerald-400 font-bold bg-[#141b2b]/40'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Spoken Script</span>
              </button>

              <button
                onClick={() => setPresenterTab('notes')}
                className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition ${
                  presenterTab === 'notes'
                    ? 'border-emerald-400 text-emerald-400 font-bold bg-[#141b2b]/40'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Notes</span>
              </button>

              <button
                onClick={() => setPresenterTab('qa')}
                className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition ${
                  presenterTab === 'qa'
                    ? 'border-emerald-400 text-emerald-400 font-bold bg-[#141b2b]/40'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>Defense Q&A</span>
                {currentSlide.defenseQuestions?.length > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full text-[9px] bg-emerald-500/20 text-emerald-300 font-bold">
                    {currentSlide.defenseQuestions.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => setPresenterTab('points')}
                className={`flex items-center space-x-1.5 px-3 py-2 border-b-2 font-medium transition ${
                  presenterTab === 'points'
                    ? 'border-emerald-400 text-emerald-400 font-bold bg-[#141b2b]/40'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Invariants</span>
              </button>
            </div>

            {/* Tab Body: Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* TAB 1: SPOKEN SCRIPT */}
              {presenterTab === 'script' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1.5">
                      <Volume2 className="w-3.5 h-3.5" />
                      READ-ALOUD VERBATIM SCRIPT
                    </span>
                    <button
                      onClick={handleCopyScript}
                      className="px-2 py-1 rounded text-[10px] font-mono bg-[#141b2b] hover:bg-[#1b2438] text-slate-300 hover:text-white border border-white/10 flex items-center gap-1 transition"
                      title="Copy script to clipboard"
                    >
                      {copiedScript ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="p-4 rounded-xl bg-[#141b2b] border border-white/10 text-slate-200 text-sm leading-relaxed whitespace-pre-line font-sans shadow-inner">
                    {currentSlide.spokenScript || currentSlide.speakerNotes || (
                      <p className="text-slate-500 italic text-xs">
                        No verbatim script assigned for this slide. Refer to Speaker Notes tab.
                      </p>
                    )}
                  </div>

                  {currentSlide.presenter?.id && (
                    <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-300/90 font-mono">
                      💡 Tip: Keep pacing steady (approx. 130 words/minute). Pause on mathematical definitions.
                    </div>
                  )}
                </div>
              )}

              {/* TAB 2: SPEAKER NOTES */}
              {presenterTab === 'notes' && (
                <div className="space-y-3">
                  <span className="text-[11px] font-mono text-slate-400">
                    SLIDE CONTEXT & PEDAGOGICAL NOTES
                  </span>
                  <div className="p-4 rounded-xl bg-[#141b2b] border border-white/10 text-slate-300 text-xs leading-relaxed space-y-2">
                    <p>{currentSlide.speakerNotes || 'No notes available for this slide.'}</p>
                  </div>

                  <div className="p-3 rounded-xl bg-[#0b0e17] border border-white/5 space-y-1.5 text-xs">
                    <span className="text-[11px] font-bold text-slate-300 font-mono">Slide Title:</span>
                    <p className="text-white font-medium">{currentSlide.title}</p>
                    <span className="text-[10px] font-mono text-slate-400 block pt-1">
                      Category: {currentSlide.category}
                    </span>
                  </div>
                </div>
              )}

              {/* TAB 3: DEFENSE Q&A */}
              {presenterTab === 'qa' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-blue-400 flex items-center gap-1.5">
                      <HelpCircle className="w-3.5 h-3.5" />
                      ANTICIPATED VIVA EXAMINER QUESTIONS
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {currentSlide.defenseQuestions?.length || 0} Questions
                    </span>
                  </div>

                  {(!currentSlide.defenseQuestions || currentSlide.defenseQuestions.length === 0) ? (
                    <div className="p-4 rounded-xl bg-[#141b2b] border border-white/10 text-center text-xs text-slate-400">
                      No specific defense questions registered for this slide.
                    </div>
                  ) : (
                    currentSlide.defenseQuestions.map((qa, qIdx) => {
                      const isExpanded = expandedQA[qIdx] ?? true; // expanded by default
                      return (
                        <div
                          key={qIdx}
                          className="rounded-xl bg-[#141b2b] border border-white/10 overflow-hidden text-xs transition"
                        >
                          <button
                            onClick={() => toggleQA(qIdx)}
                            className="w-full p-3 text-left font-semibold text-white bg-[#182135] hover:bg-[#1e2a44] flex items-start justify-between gap-2 transition"
                          >
                            <span className="text-slate-100 font-mono leading-snug">
                              Q{qIdx + 1}: {qa.question}
                            </span>
                            <span className="text-slate-400 shrink-0 font-mono text-[10px]">
                              {isExpanded ? '▲' : '▼'}
                            </span>
                          </button>

                          {isExpanded && (
                            <div className="p-3.5 text-slate-300 leading-relaxed border-t border-white/10 bg-[#141b2b] text-[11px]">
                              <span className="font-bold text-emerald-400 font-mono block mb-1">
                                Defended Answer:
                              </span>
                              {qa.answer}
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* TAB 4: INVARIANTS & TAKEAWAYS */}
              {presenterTab === 'points' && (
                <div className="space-y-3">
                  <span className="text-[11px] font-mono text-amber-400 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    ACADEMIC INVARIANTS & TAKEAWAYS
                  </span>

                  {currentSlide.keyPoints?.length > 0 ? (
                    <ul className="space-y-2">
                      {currentSlide.keyPoints.map((point, pIdx) => (
                        <li
                          key={pIdx}
                          className="p-3 rounded-lg bg-[#141b2b] border border-white/10 text-xs text-slate-200 flex items-start gap-2.5"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0 mt-1.5" />
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="p-4 rounded-xl bg-[#141b2b] border border-white/10 space-y-2 text-xs font-mono">
                      <div className="text-emerald-400 font-bold">TraceGuard AI Theoretical Invariants:</div>
                      <div className="text-slate-300">• 9 States: IDLE, CONNECTED, REQ_RCVD, AUTH_CHK, AUTH_FAIL, RESP_SENT, ERR, CLOSED, TRAP</div>
                      <div className="text-slate-300">• 13 Input Symbols: Exact network protocol events</div>
                      <div className="text-slate-300">• 117 Total Transitions (Complete Transition Matrix)</div>
                      <div className="text-slate-300">• O(1) step lookup, O(|w|) total sequence decidability</div>
                      <div className="text-slate-300">• Absorbing TRAP state with self-loops</div>
                      <div className="text-slate-300">• Hybrid formula: S_h = 0.6*S_FSM + 0.4*S_ML with 60% invariant floor</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </aside>
        )}
      </main>

      {/* ── BOTTOM THUMBNAIL STRIP (EXPANDABLE) ────────────────────── */}
      {showThumbnails && (
        <div
          ref={thumbnailStripRef}
          className="h-24 px-4 py-2 border-t border-white/10 bg-[#0b0e17] flex items-center space-x-3 overflow-x-auto shrink-0 z-20"
        >
          {slides.map((s, idx) => {
            const isActive = idx === currentIdx;
            const sTheme = PRESENTER_THEMES[s.presenter?.id || 'P1'] || PRESENTER_THEMES.P1;

            return (
              <button
                key={s.id || idx}
                ref={isActive ? activeThumbnailRef : null}
                onClick={() => setCurrentIdx(idx)}
                aria-label={`Jump to slide ${idx + 1}: ${s.title}`}
                className={`relative group shrink-0 h-20 aspect-[16/9] rounded-lg overflow-hidden border-2 transition-all duration-200 ${
                  isActive
                    ? 'border-emerald-400 ring-2 ring-emerald-400/40 scale-105 shadow-lg shadow-emerald-500/20'
                    : 'border-white/10 hover:border-white/30 opacity-70 hover:opacity-100'
                }`}
              >
                {/* Thumbnail Image */}
                <img
                  src={s.image || s.imageAsset || `/slides/slide_${String(idx + 1).padStart(2, '0')}.png`}
                  alt={`Thumbnail ${idx + 1}`}
                  className="w-full h-full object-cover bg-black"
                  loading="lazy"
                />

                {/* Overlay Badge: Slide Index */}
                <div className="absolute top-1 left-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-black/80 text-white backdrop-blur-xs">
                  {idx + 1}
                </div>

                {/* Overlay Badge: Presenter Pill */}
                <div
                  className={`absolute bottom-1 right-1 px-1.5 py-0.5 rounded text-[8px] font-mono font-bold backdrop-blur-xs ${sTheme.badge}`}
                >
                  {s.presenter?.id || 'P1'}
                </div>

                {/* Active Indicator Line */}
                {isActive && (
                  <div className="absolute inset-x-0 bottom-0 h-1 bg-emerald-400" />
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* ── BOTTOM CONTROL BAR & KEYBOARD SHORTCUTS ────────────────── */}
      <footer className="h-12 px-4 sm:px-6 border-t border-white/10 bg-[#0e131f] flex items-center justify-between text-xs font-mono shrink-0 z-20">
        {/* Left: Previous Button */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handlePrev}
            disabled={currentIdx === 0}
            className="px-3 py-1.5 rounded-lg bg-[#141b2b] hover:bg-[#1b2438] text-white disabled:opacity-30 disabled:pointer-events-none border border-white/10 hover:border-white/20 transition flex items-center space-x-1.5"
            aria-label="Previous slide"
          >
            <ChevronLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Prev</span>
          </button>

          <button
            onClick={handleNext}
            disabled={currentIdx === totalSlides - 1}
            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-30 disabled:pointer-events-none transition flex items-center space-x-1.5 font-bold shadow-md shadow-emerald-500/20"
            aria-label="Next slide"
          >
            <span className="hidden sm:inline">Next</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Center: Slide indicator & Title (Hidden on tiny screens) */}
        <div className="hidden md:flex items-center space-x-2 text-slate-300 truncate max-w-md">
          <span className="font-bold text-white truncate">{currentSlide.title}</span>
        </div>

        {/* Right: Keyboard Shortcuts Reference Legend */}
        <div className="hidden sm:flex items-center space-x-3 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 rounded bg-[#141b2b] border border-white/10 text-[10px] text-slate-300">Space</kbd>
            <kbd className="px-1.5 py-0.5 rounded bg-[#141b2b] border border-white/10 text-[10px] text-slate-300">→</kbd>
            <span>Next</span>
          </span>
          <span className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 rounded bg-[#141b2b] border border-white/10 text-[10px] text-slate-300">F</kbd>
            <span>Full</span>
          </span>
          <span className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 rounded bg-[#141b2b] border border-white/10 text-[10px] text-slate-300">Esc</kbd>
            <span>Exit</span>
          </span>
        </div>
      </footer>
    </div>
  );
}

export default PresentationMode;
