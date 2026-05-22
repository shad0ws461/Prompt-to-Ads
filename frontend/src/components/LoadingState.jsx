import React, { useState, useEffect } from 'react';

const LOADING_STEPS = [
  "Analyzing business description & intent...",
  "Querying OpenAI GPT-4o model...",
  "Structuring audience demographic matrices...",
  "Refining keyword match types & negatives...",
  "Engineering responsive search ad layouts...",
  "Preparing final Google Ads schema validation..."
];

export default function LoadingState() {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Step rotation interval
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
    }, 2500);

    // Progress bar simulation interval
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 98) return prev;
        // Slower progress as it gets near the end
        const increment = prev > 80 ? 0.5 : prev > 50 ? 1.5 : 3;
        return Math.min(prev + increment, 98);
      });
    }, 100);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center p-8 min-h-[400px]">
      {/* Outer Glow Orb */}
      <div className="relative mb-8 w-24 h-24">
        <div className="absolute inset-0 bg-blue-500 rounded-full blur-xl opacity-30 animate-pulse"></div>
        <div className="absolute inset-0 rounded-full border-4 border-slate-800 border-t-blue-500 border-r-indigo-500 animate-spin"></div>
        <div className="absolute inset-2 bg-slate-900 rounded-full flex items-center justify-center border border-slate-800">
          <svg className="w-8 h-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>

      <div className="text-center max-w-md w-full">
        <h3 className="text-xl font-semibold text-slate-100 mb-2">Generating Your Campaign</h3>
        
        {/* Step status */}
        <div className="h-6 overflow-hidden mb-6">
          <p className="text-slate-400 text-sm animate-bounce text-ellipsis overflow-hidden whitespace-nowrap">
            {LOADING_STEPS[currentStep]}
          </p>
        </div>

        {/* Progress bar container */}
        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        <div className="flex justify-between text-xs text-slate-500 px-1">
          <span>AI Orchestration</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </div>
    </div>
  );
}
