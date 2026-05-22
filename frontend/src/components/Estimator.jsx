import React, { useMemo } from 'react';

export default function Estimator({ budget, location, campaignType, keywordsCount }) {
  // Compute estimates dynamically using budget and location as factor variables
  const estimates = useMemo(() => {
    // Detect Indian location to switch currency and CPC ranges
    const isIndia = location && (
      location.toLowerCase().includes('india') || 
      location.toLowerCase().includes('delhi') || 
      location.toLowerCase().includes('mumbai') || 
      location.toLowerCase().includes('bangalore') ||
      location.toLowerCase().includes('chennai') ||
      location.toLowerCase().includes('kolkata') ||
      location.toLowerCase().includes('hyderabad') ||
      location.toLowerCase().includes('pune')
    );

    const currencySymbol = isIndia ? '₹' : '$';

    // Generate base metrics
    // India CPC range: ₹12 - ₹45 (base ₹18)
    // US/Global CPC range: $1.20 - $4.50 (base $1.65)
    let baseCPC = isIndia ? 18.50 : 1.65;
    let baseCTR = 3.8; // percentage
    let baseConvRate = 2.4; // percentage

    // Adjust based on campaign type
    if (campaignType === 'DISPLAY') {
      baseCPC = isIndia ? 6.20 : 0.65;
      baseCTR = 0.9;
      baseConvRate = 1.1;
    } else if (campaignType === 'PERFORMANCE_MAX') {
      baseCPC = isIndia ? 24.50 : 1.95;
      baseCTR = 4.2;
      baseConvRate = 3.1;
    }

    // Adjust based on location popularity
    if (location && !isIndia) {
      const loc = location.toLowerCase();
      if (loc.includes('us') || loc.includes('united states') || loc.includes('york') || loc.includes('london')) {
        baseCPC *= 1.45; // Higher bidding competition
      }
    } else if (location && isIndia) {
      const loc = location.toLowerCase();
      if (loc.includes('delhi') || loc.includes('mumbai') || loc.includes('bangalore')) {
        baseCPC *= 1.25; // Higher bidding competition in Tier 1 Indian cities
      }
    }

    // Adjust slightly based on keyword count
    if (keywordsCount > 0) {
      baseCPC += isIndia ? Math.min(keywordsCount * 0.25, 4.0) : Math.min(keywordsCount * 0.02, 0.30);
    }

    // Final calculations
    const dailyBudget = parseFloat(budget) || 10;
    const clicks = Math.max(Math.floor(dailyBudget / baseCPC), 1);
    const impressions = Math.floor((clicks / (baseCTR / 100)));
    const conversions = (clicks * (baseConvRate / 100)).toFixed(1);

    return {
      currencySymbol,
      avgCPC: baseCPC.toFixed(2),
      ctr: baseCTR.toFixed(1),
      clicks,
      impressions,
      conversions
    };
  }, [budget, location, campaignType, keywordsCount]);

  return (
    <div className="glass-card rounded-xl p-6 border border-slate-800">
      <h4 className="text-md font-medium text-slate-200 mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Keyword Cost & Reach Estimator
      </h4>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800/40">
          <p className="text-xs text-slate-500 mb-0.5">Est. Daily Clicks</p>
          <p className="text-xl font-bold text-slate-100">{estimates.clicks}</p>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800/40">
          <p className="text-xs text-slate-500 mb-0.5">Est. Daily Impressions</p>
          <p className="text-xl font-bold text-slate-100">{estimates.impressions.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800/40">
          <p className="text-xs text-slate-500 mb-0.5">Average Cost Per Click</p>
          <p className="text-xl font-bold text-indigo-400">{estimates.currencySymbol}{estimates.avgCPC}</p>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800/40">
          <p className="text-xs text-slate-500 mb-0.5">Est. Conversions / Day</p>
          <p className="text-xl font-bold text-emerald-400">{estimates.conversions}</p>
        </div>
      </div>

      <div className="text-xs text-slate-500 border-t border-slate-800/60 pt-3 flex justify-between items-center">
        <span>Click-Through Rate (CTR): <strong>{estimates.ctr}%</strong></span>
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Live Projection
        </span>
      </div>
    </div>
  );
}
