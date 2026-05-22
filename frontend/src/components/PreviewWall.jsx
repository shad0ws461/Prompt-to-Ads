import React, { useState } from 'react';

export default function PreviewWall({ campaignData, onUpdate, onDeploy, dailyBudget, websiteUrl, targetLocation }) {
  const [activeVariantIdx, setActiveVariantIdx] = useState(0);
  const [newKeyword, setNewKeyword] = useState('');
  const [newNegKeyword, setNewNegKeyword] = useState('');

  const currentVariant = campaignData.ad_variants[activeVariantIdx] || { headlines: ['', '', ''], descriptions: ['', ''] };

  // Sync edits back to App level
  const handleHeadlineChange = (idx, value) => {
    const updatedVariants = [...campaignData.ad_variants];
    updatedVariants[activeVariantIdx] = {
      ...currentVariant,
      headlines: currentVariant.headlines.map((h, i) => (i === idx ? value : h))
    };
    onUpdate({ ...campaignData, ad_variants: updatedVariants });
  };

  const handleDescriptionChange = (idx, value) => {
    const updatedVariants = [...campaignData.ad_variants];
    updatedVariants[activeVariantIdx] = {
      ...currentVariant,
      descriptions: currentVariant.descriptions.map((d, i) => (i === idx ? value : d))
    };
    onUpdate({ ...campaignData, ad_variants: updatedVariants });
  };

  const handleAddKeyword = (e) => {
    e.preventDefault();
    if (!newKeyword.trim()) return;
    onUpdate({
      ...campaignData,
      keywords: [...campaignData.keywords, newKeyword.trim()]
    });
    setNewKeyword('');
  };

  const handleRemoveKeyword = (kwToRemove) => {
    onUpdate({
      ...campaignData,
      keywords: campaignData.keywords.filter((kw) => kw !== kwToRemove)
    });
  };

  const handleAddNegKeyword = (e) => {
    e.preventDefault();
    if (!newNegKeyword.trim()) return;
    onUpdate({
      ...campaignData,
      negative_keywords: [...campaignData.negative_keywords, newNegNegKeyword.trim()]
    });
    setNewNegKeyword('');
  };

  const handleRemoveNegKeyword = (kwToRemove) => {
    onUpdate({
      ...campaignData,
      negative_keywords: campaignData.negative_keywords.filter((kw) => kw !== kwToRemove)
    });
  };

  // Safe checks for warning labels
  const getCharLimitClass = (currentLength, limit) => {
    if (currentLength > limit) return 'text-rose-500 font-semibold';
    if (currentLength === limit) return 'text-amber-500';
    return 'text-slate-400';
  };

  const cleanUrl = (url) => {
    if (!url) return 'www.your-business.com';
    return url.replace(/^(https?:\/\/)?(www\.)?/, '').split('/')[0];
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Editor Column */}
      <div className="lg:col-span-7 flex flex-col gap-6">
        <div className="glass-card rounded-xl p-6 border border-slate-800">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-slate-100">Review & Edit Campaign</h3>
            <div className="flex bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/50">
              {campaignData.ad_variants.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveVariantIdx(idx)}
                  className={`px-3 py-1 text-xs rounded-md transition-all font-medium ${
                    activeVariantIdx === idx
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Variant {idx + 1}
                </button>
              ))}
            </div>
          </div>

          {/* Ad Copy Editor */}
          <div className="space-y-4 mb-6">
            <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Ad Variant Copy</h4>
            
            {/* Headlines */}
            <div className="space-y-3">
              <label className="block text-xs text-slate-400 font-medium">Headlines (Exactly 3 - Max 30 chars each)</label>
              {currentVariant.headlines.map((headline, idx) => (
                <div key={idx} className="relative">
                  <input
                    type="text"
                    value={headline}
                    maxLength={40} // Allow typing a bit over to trigger warning styling
                    onChange={(e) => handleHeadlineChange(idx, e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 pr-16 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                    placeholder={`Headline ${idx + 1}`}
                  />
                  <span className={`absolute right-3 top-2.5 text-xs ${getCharLimitClass(headline.length, 30)}`}>
                    {headline.length}/30
                  </span>
                </div>
              ))}
            </div>

            {/* Descriptions */}
            <div className="space-y-3 pt-2">
              <label className="block text-xs text-slate-400 font-medium">Descriptions (Exactly 2 - Max 90 chars each)</label>
              {currentVariant.descriptions.map((desc, idx) => (
                <div key={idx} className="relative">
                  <textarea
                    rows={2}
                    value={desc}
                    maxLength={110} // Allow slightly over to trigger warning styling
                    onChange={(e) => handleDescriptionChange(idx, e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 pr-16 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
                    placeholder={`Description ${idx + 1}`}
                  />
                  <span className={`absolute right-3 bottom-2 text-xs ${getCharLimitClass(desc.length, 90)}`}>
                    {desc.length}/90
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Keywords & Negatives Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800/80">
            {/* Target Keywords */}
            <div>
              <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">Intent-Based Keywords</h4>
              <form onSubmit={handleAddKeyword} className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  placeholder="Add target keyword..."
                />
                <button type="submit" className="bg-indigo-600/80 hover:bg-indigo-600 text-white px-3 py-1 rounded-lg text-xs font-medium transition-all">
                  Add
                </button>
              </form>
              <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto pr-1">
                {campaignData.keywords.map((kw, i) => (
                  <span key={i} className="inline-flex items-center gap-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded text-xs">
                    {kw}
                    <button type="button" onClick={() => handleRemoveKeyword(kw)} className="text-indigo-400 hover:text-rose-400 font-bold ml-1">
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Negative Keywords */}
            <div>
              <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2">Negative Keywords</h4>
              <form onSubmit={handleAddNegKeyword} className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newNegKeyword}
                  onChange={(e) => setNewNegKeyword(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                  placeholder="Add filter negative..."
                />
                <button type="submit" className="bg-rose-900/40 hover:bg-rose-900/60 border border-rose-800 text-rose-300 px-3 py-1 rounded-lg text-xs font-medium transition-all">
                  Add
                </button>
              </form>
              <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto pr-1">
                {campaignData.negative_keywords.map((neg, i) => (
                  <span key={i} className="inline-flex items-center gap-1 bg-rose-500/10 border border-rose-500/20 text-rose-300 px-2 py-0.5 rounded text-xs">
                    {neg}
                    <button type="button" onClick={() => handleRemoveNegKeyword(neg)} className="text-rose-400 hover:text-rose-600 font-bold ml-1">
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Mock Column */}
      <div className="lg:col-span-5 flex flex-col gap-6">
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-1">
            Google Search Preview (Desktop)
          </h4>
          
          {/* Google Search Mock Frame */}
          <div className="bg-white text-slate-900 rounded-xl p-5 shadow-2xl border border-slate-200 flex flex-col gap-3 font-sans">
            {/* Header info */}
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="font-bold text-slate-800 bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 text-[10px]">
                Sponsored
              </span>
              <span className="hover:underline cursor-pointer truncate max-w-[200px]">
                {cleanUrl(websiteUrl)}
              </span>
              <span>•</span>
              <span className="cursor-pointer">Ad</span>
            </div>

            {/* Google Search Headline (blue link) */}
            <div className="text-lg md:text-xl text-[#1a0dab] hover:underline cursor-pointer leading-tight font-medium font-sans">
              {currentVariant.headlines.filter(h => h.trim().length > 0).join(' | ') || 'Your Custom Campaign Headlines'}
            </div>

            {/* Google Search Descriptions (gray text) */}
            <div className="text-sm text-[#4d5156] leading-relaxed break-words font-sans">
              {currentVariant.descriptions.filter(d => d.trim().length > 0).join(' ') || 'Insert ad copy details dynamically configured based on your text prompts.'}
            </div>

            {/* Visual sitelinks decorations */}
            <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 border-t border-slate-100 pt-3 mt-1 text-xs">
              <div>
                <span className="text-[#1a0dab] hover:underline cursor-pointer font-medium">Order Online</span>
                <p className="text-slate-500 text-[11px] truncate">Fast delivery options available.</p>
              </div>
              <div>
                <span className="text-[#1a0dab] hover:underline cursor-pointer font-medium">Contact Us</span>
                <p className="text-slate-500 text-[11px] truncate">Get assistance 24/7 client support.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Deploy Button */}
        <button
          onClick={onDeploy}
          className="glow-btn bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold py-4 px-6 rounded-xl shadow-lg shadow-indigo-900/30 transition-all flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          Deploy to Google Ads Account
        </button>
      </div>
    </div>
  );
}
