const { useState, useRef, useEffect } = React;

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);

    const EXAMPLE_QUESTIONS = [
        "What are the stages of an Indian election?",
        "Who is eligible to register as a voter?",
        "What is the Model Code of Conduct?",
        "What is the role of a Booth Level Officer?"
    ];

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleExampleClick = (q) => {
        setInput(q);
        if (textareaRef.current) textareaRef.current.focus();
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isLoading) return;

        const currentInput = input.trim();
        const userMessage = { role: 'user', content: currentInput };
        
        setError(null);
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Prepare history (last 5 pairs)
        const historyContext = messages.slice(-10).map(m => ({
            role: m.role,
            parts: [{ text: m.content }]
        }));

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: currentInput,
                    history: historyContext
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            setMessages(prev => [...prev, { role: 'model', content: data.response }]);
        } catch (err) {
            console.error("Error:", err);
            setError({
                message: "Unable to connect to the educational server. Please check your connection.",
                retryData: currentInput
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleRetry = () => {
        if (error?.retryData) {
            setInput(error.retryData);
            setError(null);
            // Re-trigger submit after setting input? 
            // Better to just let user hit enter/click ask again with the populated field
        }
    };

    const formatMessage = (text) => {
        let formatted = text.replace(/\n/g, '<br/>');
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        return { __html: formatted };
    };

    return (
        <div className="flex flex-col h-full w-full max-w-4xl mx-auto bg-white sm:my-4 sm:rounded-2xl sm:shadow-2xl sm:border border-slate-200 overflow-hidden relative">
            {/* Hero Strip */}
            <header className="bg-gradient-to-r from-blue-700 to-teal-600 px-6 py-8 text-white shadow-md">
                <div className="flex flex-col space-y-1">
                    <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">ElectEd India</h1>
                    <p className="text-blue-50 font-medium opacity-90">Your Guide to the Indian Election Process</p>
                </div>
            </header>

            {/* Chat Surface */}
            <main className="flex-1 overflow-y-auto bg-slate-50/30 p-4 sm:p-8 space-y-8" aria-live="polite">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-8 py-12">
                        <div className="space-y-4 max-w-lg">
                            <h2 className="text-xl font-semibold text-slate-800">Welcome to your educational guide</h2>
                            <p className="text-slate-600 leading-relaxed text-balance">
                                I can explain how elections work in India, who can vote, and the official processes involved. 
                                Ask any question to get started.
                            </p>
                        </div>
                        
                        <div className="w-full max-w-md">
                            <p className="text-xs font-bold text-slate-600 uppercase tracking-widest mb-4">Try asking about</p>
                            <div className="flex flex-wrap justify-center gap-2">
                                {EXAMPLE_QUESTIONS.map((q, i) => (
                                    <button 
                                        key={i}
                                        onClick={() => handleExampleClick(q)}
                                        className="text-sm px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-full hover:border-blue-400 hover:text-blue-700 hover:bg-blue-50 transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
                                    >
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div 
                            className={`max-w-[90%] sm:max-w-[80%] rounded-2xl px-6 py-4 shadow-sm ${
                                msg.role === 'user' 
                                ? 'bg-blue-600 text-white rounded-br-none' 
                                : 'bg-white border border-slate-100 text-slate-800 rounded-bl-none'
                            }`}
                        >
                            {msg.role === 'user' ? (
                                <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
                            ) : (
                                <div className="markdown-body text-[16px] leading-relaxed space-y-3" dangerouslySetInnerHTML={formatMessage(msg.content)} />
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-100 rounded-2xl rounded-bl-none px-6 py-4 text-slate-400 flex space-x-1.5 shadow-sm" aria-label="Preparing explanation...">
                            <div className="w-2.5 h-2.5 bg-slate-200 rounded-full animate-bounce"></div>
                            <div className="w-2.5 h-2.5 bg-slate-300 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                            <div className="w-2.5 h-2.5 bg-slate-200 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="max-w-md mx-auto bg-rose-50 border border-rose-200 rounded-xl p-4 flex flex-col items-center space-y-3 shadow-sm">
                        <p className="text-sm text-rose-800 text-center font-medium">{error.message}</p>
                        <button 
                            onClick={handleRetry}
                            className="text-xs px-4 py-2 bg-white border border-rose-200 text-rose-700 rounded-lg hover:bg-rose-100 transition-colors font-bold uppercase tracking-wider focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2"
                        >
                            Retry Request
                        </button>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </main>

            {/* Input Bar */}
            <footer className="border-t border-slate-100 bg-white p-4 sm:p-6 shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.05)]">
                <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="flex flex-col space-y-3">
                    <div className="relative flex items-end shadow-md border-2 border-slate-200 rounded-2xl overflow-hidden focus-within:border-blue-500 bg-white transition-colors">
                        <textarea
                            ref={textareaRef}
                            className="w-full max-h-40 min-h-[60px] py-4 pl-5 pr-14 resize-none outline-none bg-transparent text-slate-800 leading-relaxed"
                            placeholder="Ask a question about the Indian election process..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            rows={1}
                            disabled={isLoading}
                            aria-label="Ask a question"
                        />
                        <button 
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="absolute right-2 bottom-2 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all transform active:scale-95 shadow-lg shadow-blue-200"
                            aria-label="Ask"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                                <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex justify-center items-center space-x-2 py-1">
                        <p className="text-[10px] sm:text-xs text-center text-slate-600 font-medium">
                            Educational tool • Not affiliated with the Election Commission of India
                        </p>
                    </div>
                </form>
            </footer>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

