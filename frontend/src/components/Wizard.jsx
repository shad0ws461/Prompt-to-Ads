import React from 'react';

const TEMPLATES = [
  {
    label: "🍰 Local Bakery",
    prompt: "A local family-owned gourmet bakery aiming to scale birthday cake orders and weekend pastry deliveries.",
    location: "Chicago, IL",
    budget: 45,
    url: "https://www.sweetcelebrationschicago.com"
  },
  {
    label: "💼 B2B SaaS",
    prompt: "B2B pipeline management software targeting mid-market marketing agencies to book interactive live product demos.",
    location: "United States",
    budget: 150,
    url: "https://www.leadflowpro.io"
  },
  {
    label: "☕ Coffee E-Commerce",
    prompt: "An organic DTC specialty coffee brand selling subscription bags of single-origin dark roast coffee beans.",
    location: "Global",
    budget: 75,
    url: "https://www.roastmastersclub.com"
  }
];

export default function Wizard({ 
  prompt, setPrompt, 
  location, setLocation, 
  budget, setBudget, 
  url, setUrl, 
  onSubmit, 
  isLoading 
}) {

  const handleApplyTemplate = (tpl) => {
    setPrompt(tpl.prompt);
    setLocation(tpl.location);
    setBudget(tpl.budget);
    setUrl(tpl.url);
  };

  return (
    <div className="glass-card rounded-2xl p-6 md:p-8 border border-slate-800 shadow-2xl max-w-4xl mx-auto">
      <h2 className="text-xl md:text-2xl font-bold text-slate-100 mb-2">Smart Campaign Input Wizard</h2>
      <p className="text-sm text-slate-400 mb-8">
        Describe your business goals below. Our AI will automatically generate optimized campaign keywords, negatives, bidding structures, and high-performance ad copy variants.
      </p>

      {/* Quick Fill Templates */}
      <div className="mb-6">
        <label className="block text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-3">
          Quick-Fill Campaign Templates
        </label>
        <div className="flex flex-wrap gap-3">
          {TEMPLATES.map((tpl, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleApplyTemplate(tpl)}
              className="px-4 py-2 rounded-xl text-sm font-medium bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-850 text-slate-300 transition-all duration-200 cursor-pointer flex items-center gap-1.5"
            >
              {tpl.label}
            </button>
          ))}
        </div>
      </div>

      {/* Primary Input Form */}
      <form onSubmit={onSubmit} className="space-y-6">
        {/* Campaign Prompt */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-medium text-slate-350" htmlFor="prompt">
              AI Campaign Prompt
            </label>
            <span className="text-xs text-slate-500">Be as descriptive as possible</span>
          </div>
          <textarea
            id="prompt"
            rows={4}
            required
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., We are a boutique fitness studio opening in downtown Austin. We want to attract local members with a 2-week free trial promotion..."
            className="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-all placeholder:text-slate-600 focus:ring-1 focus:ring-indigo-500/30"
          ></textarea>
        </div>

        {/* Advanced Optional Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Target Location */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-350" htmlFor="location">
              Target Location <span className="text-slate-600">(Optional)</span>
            </label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Chicago, IL or United States"
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-all placeholder:text-slate-600"
            />
          </div>

          {/* Daily Budget */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-350" htmlFor="budget">
              Daily Budget (USD)
            </label>
            <div className="relative">
              <span className="absolute left-4 top-2.5 text-slate-500 text-sm">$</span>
              <input
                id="budget"
                type="number"
                min="5"
                max="5000"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-8 pr-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>

          {/* Website Landing URL */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-350" htmlFor="url">
              Website URL <span className="text-slate-600">(Optional)</span>
            </label>
            <input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-all placeholder:text-slate-600"
            />
          </div>
        </div>

        {/* Submit Action */}
        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="glow-btn px-8 py-3.5 rounded-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-indigo-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 cursor-pointer"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </>
            ) : (
              <>
                Generate Campaign Assets
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
