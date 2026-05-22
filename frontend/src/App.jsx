import React, { useState } from 'react';
import Wizard from './components/Wizard';
import LoadingState from './components/LoadingState';
import PreviewWall from './components/PreviewWall';
import Estimator from './components/Estimator';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function App() {
  const [appState, setAppState] = useState('idle'); // idle | loading | preview | deployed
  
  // Form parameters
  const [prompt, setPrompt] = useState('');
  const [location, setLocation] = useState('');
  const [budget, setBudget] = useState(50);
  const [url, setUrl] = useState('');
  const [campaignName, setCampaignName] = useState('');

  // AI & Deployment data
  const [campaignData, setCampaignData] = useState(null);
  const [deployResult, setDeployResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [isAccountLinked, setIsAccountLinked] = useState(false);

  // Authentication trigger
  const handleLinkAccount = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/oauth/url`);
      const data = await res.json();
      if (data.url) {
        // Open OAuth URL in a new window or tab
        window.open(data.url, '_blank');
        setIsAccountLinked(true);
      }
    } catch (err) {
      console.error("Failed to fetch OAuth URL:", err);
      setErrorMsg("Failed to connect to Google OAuth service.");
    }
  };

  // Generate Assets
  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setAppState('loading');
    setErrorMsg('');
    
    // Automatically set a campaign name based on prompt
    const cleanName = prompt.split(' ').slice(0, 3).join(' ') + ' AI Campaign';
    setCampaignName(cleanName.replace(/[^\w\s]/gi, ''));

    try {
      const response = await fetch(`${API_BASE}/api/generate-campaign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          target_location: location || null,
          daily_budget: parseFloat(budget) || 50.0,
          website_url: url || null
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned code ${response.status}`);
      }

      const resJson = await response.json();
      if (resJson.success) {
        setCampaignData(resJson.data);
        setAppState('preview');
      } else {
        throw new Error(resJson.detail || "Unknown generation error");
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(`Failed to generate campaign. Ensure backend is running at ${API_BASE}.`);
      setAppState('idle');
    }
  };

  // Deploy Campaign
  const handleDeploy = async () => {
    if (!campaignData) return;
    setErrorMsg('');

    try {
      const response = await fetch(`${API_BASE}/api/deploy-campaign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_data: campaignData,
          campaign_name: campaignName,
          daily_budget: parseFloat(budget),
          website_url: url || null,
          target_location: location || null
        })
      });

      const resJson = await response.json();
      if (response.ok && resJson.success) {
        setDeployResult(resJson);
        setAppState('deployed');
      } else {
        throw new Error(resJson.detail?.message || "Failed to complete deployment operations.");
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Failed to deploy campaign.");
    }
  };

  const handleReset = () => {
    setPrompt('');
    setLocation('');
    setBudget(50);
    setUrl('');
    setCampaignData(null);
    setDeployResult(null);
    setErrorMsg('');
    setAppState('idle');
  };

  return (
    <div className="min-h-screen text-slate-100 flex flex-col">
      {/* Navigation Header */}
      <header className="glass-panel border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 font-bold">
              P
            </div>
            <div>
              <span className="font-extrabold text-base tracking-tight bg-gradient-to-r from-slate-100 to-slate-350 bg-clip-text text-transparent">
                Prompt-to-Ads
              </span>
              <span className="text-[10px] block text-slate-500 font-mono tracking-wider uppercase -mt-0.5">
                AI Ads Architect
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Account Status Badge */}
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isAccountLinked ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
              <span className="text-xs text-slate-400 font-medium">
                {isAccountLinked ? 'Google Ads Linked' : 'Sandbox Demo Mode'}
              </span>
            </div>

            {!isAccountLinked && (
              <button
                onClick={handleLinkAccount}
                className="bg-slate-850 hover:bg-slate-800 border border-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition-all text-slate-200 cursor-pointer"
              >
                Link Ads Account
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        
        {/* Error Banners */}
        {errorMsg && (
          <div className="max-w-4xl mx-auto mb-6 bg-rose-500/10 border border-rose-500/20 rounded-xl p-4 flex gap-3 items-center">
            <svg className="w-5 h-5 text-rose-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="text-sm text-rose-350">{errorMsg}</p>
          </div>
        )}

        {/* Wizard Input Screen */}
        {appState === 'idle' && (
          <Wizard
            prompt={prompt}
            setPrompt={setPrompt}
            location={location}
            setLocation={setLocation}
            budget={budget}
            setBudget={setBudget}
            url={url}
            setUrl={setUrl}
            onSubmit={handleGenerate}
            isLoading={false}
          />
        )}

        {/* Loading Generation Screen */}
        {appState === 'loading' && <LoadingState />}

        {/* Campaign Assets Preview Wall */}
        {appState === 'preview' && campaignData && (
          <div className="space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-5">
              <div>
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-widest">Workspace Dashboard</span>
                <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
                  Campaign Generation Review:
                  <input
                    type="text"
                    value={campaignName}
                    onChange={(e) => setCampaignName(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded px-2.5 py-0.5 text-lg font-bold text-indigo-300 focus:outline-none focus:border-indigo-600 max-w-[280px] md:max-w-md"
                  />
                </h1>
              </div>
              <button
                onClick={handleReset}
                className="bg-slate-900 hover:bg-slate-850 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700 px-4 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer"
              >
                ← Clear & Start Over
              </button>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
              {/* Main Preview and Editor Wall */}
              <div className="xl:col-span-8">
                <PreviewWall
                  campaignData={campaignData}
                  onUpdate={setCampaignData}
                  onDeploy={handleDeploy}
                  dailyBudget={budget}
                  websiteUrl={url}
                  targetLocation={location}
                />
              </div>

              {/* Side Estimator Panel */}
              <div className="xl:col-span-4">
                <Estimator
                  budget={budget}
                  location={location}
                  campaignType={campaignData.campaign_type}
                  keywordsCount={campaignData.keywords.length}
                />
              </div>
            </div>
          </div>
        )}

        {/* Campaign Deployed Screen */}
        {appState === 'deployed' && deployResult && (
          <div className="glass-card rounded-2xl p-6 md:p-10 border border-slate-800 shadow-2xl max-w-4xl mx-auto text-center flex flex-col items-center">
            {/* Green Badge Animation */}
            <div className="relative mb-6 w-20 h-20">
              <div className="absolute inset-0 bg-emerald-500 rounded-full blur-lg opacity-25"></div>
              <div className="absolute inset-0 bg-emerald-950/40 border-2 border-emerald-500 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-emerald-400 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-slate-100 mb-2">Campaign Deployed Successfully!</h2>
            <p className="text-slate-400 text-sm max-w-md mb-8">
              Your AI-generated assets have been successfully structured and pushed into Google Ads API resources.
            </p>

            {/* Resources list */}
            <div className="w-full text-left bg-slate-900/60 border border-slate-850 rounded-xl p-5 mb-8">
              <h3 className="text-xs font-semibold text-indigo-400 uppercase tracking-widest mb-4">Generated API Resource Handles</h3>
              <div className="space-y-3.5 text-sm font-mono">
                <div className="flex flex-col md:flex-row md:justify-between border-b border-slate-800/40 pb-2">
                  <span className="text-slate-500 text-xs">Campaign Budget:</span>
                  <span className="text-slate-300 font-bold truncate max-w-full md:max-w-md">{deployResult.resource_names.campaign_budget}</span>
                </div>
                <div className="flex flex-col md:flex-row md:justify-between border-b border-slate-800/40 pb-2">
                  <span className="text-slate-500 text-xs">Campaign Resource:</span>
                  <span className="text-indigo-400 font-bold truncate max-w-full md:max-w-md">{deployResult.resource_names.campaign}</span>
                </div>
                <div className="flex flex-col md:flex-row md:justify-between border-b border-slate-800/40 pb-2">
                  <span className="text-slate-500 text-xs">Ad Group Resource:</span>
                  <span className="text-slate-300 font-bold truncate max-w-full md:max-w-md">{deployResult.resource_names.ad_group}</span>
                </div>
                <div className="flex flex-col md:flex-row md:justify-between pb-1">
                  <span className="text-slate-500 text-xs">Ad Variants Count:</span>
                  <span className="text-emerald-400 font-bold">{deployResult.resource_names.ads.length} Ads Created</span>
                </div>
              </div>
            </div>

            {/* Sandbox Details / Dry Run Payload Tracer */}
            {deployResult.is_mock && (
              <div className="w-full text-left bg-slate-950 border border-slate-900 rounded-xl p-5 mb-8 overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xs font-semibold text-rose-400 uppercase tracking-widest">
                    Google Ads API SDK Request Trace (Dry Run)
                  </h3>
                  <span className="bg-rose-950 border border-rose-800 text-[10px] text-rose-300 px-2 py-0.5 rounded font-mono font-bold">
                    API SCHEMA TRACE
                  </span>
                </div>
                <div className="max-h-60 overflow-y-auto pr-1">
                  {deployResult.simulation_details.map((stepData, index) => (
                    <div key={index} className="mb-4 last:mb-0">
                      <p className="text-xs font-bold text-slate-400 border-b border-slate-900 pb-1 mb-2">
                        {stepData.step}
                      </p>
                      <pre className="text-[11px] text-emerald-500 font-mono overflow-x-auto whitespace-pre bg-slate-900/40 p-2.5 rounded border border-slate-900/60 leading-normal">
                        {JSON.stringify(stepData.payload || stepData.payloads, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={handleReset}
              className="glow-btn bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 px-8 rounded-xl shadow-lg shadow-indigo-900/20 transition-all cursor-pointer"
            >
              Configure Another Campaign
            </button>
          </div>
        )}

      </main>

      {/* Footer Info */}
      <footer className="border-t border-slate-900 py-6 mt-12 bg-slate-950/20 text-center text-xs text-slate-650">
        <p>© 2026 Prompt-to-Ads AI. Built for automated digital marketing campaign deployment.</p>
      </footer>
    </div>
  );
}
