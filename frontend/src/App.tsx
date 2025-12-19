import { useState, useEffect } from 'react';
import { Zap, Copy, Save, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { enhancePrompt, getPromptHistory, type EnhancedPromptResponse } from './services/promptService';
import { getTemplates, type Template } from './services/templateService';

export default function App() {
  const [inputPrompt, setInputPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EnhancedPromptResponse | null>(null);
  const [error, setError] = useState('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showTemplates, setShowTemplates] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  
  // Advanced settings
  const [temperature, setTemperature] = useState(0.3);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [customSystemPrompt, setCustomSystemPrompt] = useState('');

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await getTemplates();
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const filteredTemplates = templates.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleEnhance = async () => {
    if (!inputPrompt.trim()) return;

    setLoading(true);
    setError('');

    try {
      // Call Django backend API
      const response = await enhancePrompt({
        prompt_text: inputPrompt,
        template_id: selectedTemplate?.id,
        temperature,
        max_tokens: maxTokens,
        custom_system_prompt: customSystemPrompt || undefined,
      });

      setResult(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 
                          err.message || 
                          'Failed to enhance prompt';
      setError(errorMessage);
      console.error('Enhancement error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrompt = async () => {
    if (!result) return;
    
    try {
      // TODO: Implement save to Django backend
      // const savedPrompt = await savePrompt({
      //   prompt_id: result.id,
      //   custom_title: inputPrompt.substring(0, 50),
      //   category: selectedTemplate?.category || 'Other',
      // });
      
      alert('✓ Prompt saved! (Feature coming soon)');
    } catch (err) {
      console.error('Save error:', err);
      setError('Failed to save prompt');
    }
  };

  const applyTemplate = (template: Template) => {
    setSelectedTemplate(template);
    setCustomSystemPrompt('');
    alert(`✓ ${template.name} template applied`);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50">
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
              <Zap className="text-cyan-500" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-50">Echo</h1>
              <p className="text-xs text-slate-400">Django + React • PTCF Engine</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {!result ? (
          // INPUT VIEW
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Input */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                <h2 className="text-3xl font-bold text-slate-50 mb-2">Transform Your Prompts</h2>
                <p className="text-lg text-slate-400">Submit weak prompts. Receive PTCF-structured enhancements powered by Django + Gemini.</p>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-300 text-sm">
                  {error}
                </div>
              )}

              {selectedTemplate && (
                <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3">
                  <p className="text-sm text-cyan-300">📌 Template: <strong>{selectedTemplate.name}</strong></p>
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-slate-50 mb-3">Your Prompt</label>
                <textarea
                  value={inputPrompt}
                  onChange={(e) => setInputPrompt(e.target.value)}
                  placeholder="Enter your weak prompt here..."
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-50 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 resize-none"
                  rows={6}
                />
                <button
                  onClick={handleEnhance}
                  disabled={!inputPrompt.trim() || loading}
                  className="mt-4 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 text-slate-900 rounded-lg font-semibold disabled:cursor-not-allowed"
                >
                  {loading ? '⏳ Processing...' : '✨ Enhance Prompt'}
                </button>
              </div>

              {loading && (
                <div className="flex flex-col items-center py-12">
                  <div className="relative h-12 w-12 mb-4">
                    <div className="absolute inset-0 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-500"></div>
                  </div>
                  <p className="text-slate-400">Backend processing with Gemini API...</p>
                </div>
              )}
            </div>

            {/* Right Column - Settings & Templates */}
            <div className="space-y-6">
              {/* Advanced Settings */}
              <div className="bg-slate-800 border border-slate-700 rounded-lg">
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="w-full p-4 flex items-center justify-between hover:bg-slate-700/50"
                >
                  <span className="font-semibold">⚙️ Advanced</span>
                  {showAdvanced ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>
                
                {showAdvanced && (
                  <div className="border-t border-slate-700 p-4 space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-2">
                        Temperature: {temperature.toFixed(1)}
                      </label>
                      <input
                        type="range"
                        min="0.1"
                        max="1"
                        step="0.1"
                        value={temperature}
                        onChange={(e) => setTemperature(parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <p className="text-xs text-slate-400 mt-1">Lower = focused, Higher = creative</p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-2">
                        Max Tokens: {maxTokens}
                      </label>
                      <input
                        type="range"
                        min="256"
                        max="4096"
                        step="256"
                        value={maxTokens}
                        onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-2">
                        Custom System Prompt
                      </label>
                      <textarea
                        value={customSystemPrompt}
                        onChange={(e) => setCustomSystemPrompt(e.target.value)}
                        placeholder="Override template..."
                        className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-slate-50 text-xs placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                        rows={3}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Templates */}
              <div className="bg-slate-800 border border-slate-700 rounded-lg">
                <button
                  onClick={() => setShowTemplates(!showTemplates)}
                  className="w-full p-4 flex items-center justify-between hover:bg-slate-700/50"
                >
                  <span className="font-semibold">📚 Templates</span>
                  {showTemplates ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>

                {showTemplates && (
                  <div className="border-t border-slate-700 p-4 space-y-3">
                    <input
                      type="text"
                      placeholder="Search..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-slate-50 text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />

                    <div className="max-h-96 overflow-y-auto space-y-2">
                      {filteredTemplates.map((template) => (
                        <button
                          key={template.id}
                          onClick={() => applyTemplate(template)}
                          className={`w-full text-left p-3 rounded text-sm transition ${
                            selectedTemplate?.id === template.id
                              ? 'bg-cyan-500/20 border border-cyan-500/50'
                              : 'bg-slate-900 border border-slate-600 hover:border-slate-500'
                          }`}
                        >
                          <p className="font-semibold text-slate-50">{template.name}</p>
                          <p className="text-xs text-slate-400">{template.category}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          // RESULTS VIEW
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold text-slate-50">✨ Enhanced Prompt</h2>
              <button
                onClick={handleSavePrompt}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold flex items-center gap-2"
              >
                <Save size={18} /> Save
              </button>
            </div>

            <div className="bg-gradient-to-r from-cyan-500/10 to-cyan-500/5 border border-cyan-500/30 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-cyan-400 mb-2">📊 Summary</h3>
              <p className="text-slate-50">{result.enhanced.improvement_summary}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <h3 className="text-sm font-bold text-slate-50 mb-3">👤 Persona</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-slate-400">Role:</span> {result.enhanced.persona.role}</div>
                  <div><span className="text-slate-400">Expertise:</span> {result.enhanced.persona.expertise}</div>
                  <div><span className="text-slate-400">Perspective:</span> {result.enhanced.persona.perspective}</div>
                </div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <h3 className="text-sm font-bold text-slate-50 mb-3">✓ Task</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-slate-400">Objective:</span> {result.enhanced.task.objective}</div>
                  <div><span className="text-slate-400">Deliverable:</span> {result.enhanced.task.deliverable}</div>
                  <div><span className="text-slate-400">Constraints:</span> {result.enhanced.task.constraints.join(', ')}</div>
                </div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <h3 className="text-sm font-bold text-slate-50 mb-3">⚙️ Context</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-slate-400">Background:</span> {result.enhanced.context.technical_background}</div>
                  <div><span className="text-slate-400">Considerations:</span> {result.enhanced.context.key_considerations.join(', ')}</div>
                  <div><span className="text-slate-400">Audience:</span> {result.enhanced.context.audience}</div>
                </div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <h3 className="text-sm font-bold text-slate-50 mb-3">📋 Format</h3>
                <div className="space-y-2 text-sm">
                  <div><span className="text-slate-400">Style:</span> {result.enhanced.format.output_style}</div>
                  <div><span className="text-slate-400">Structure:</span> {result.enhanced.format.structure.join(', ')}</div>
                  <div><span className="text-slate-400">Tone:</span> {result.enhanced.format.tone}</div>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-slate-50">🚀 Production-Ready Prompt</h3>
                <button
                  onClick={() => navigator.clipboard.writeText(result.enhanced.consolidated_prompt)}
                  className="px-3 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded text-cyan-400 text-xs font-semibold flex items-center gap-1"
                >
                  <Copy size={14} /> Copy
                </button>
              </div>
              <div className="bg-slate-900 rounded p-3 border border-slate-700 max-h-96 overflow-y-auto">
                <p className="text-slate-100 text-sm font-mono whitespace-pre-wrap break-words">
                  {result.enhanced.consolidated_prompt}
                </p>
              </div>
            </div>

            <button
              onClick={() => { setResult(null); setInputPrompt(''); setSearchQuery(''); }}
              className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-slate-900 rounded-lg font-semibold"
            >
              ✨ Enhance Another Prompt
            </button>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-900/50 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8 text-center text-sm text-slate-500">
          Echo • Full-Stack (Django + React) • Powered by Gemini 2.5 Flash
        </div>
      </footer>
    </div>
  );
}
