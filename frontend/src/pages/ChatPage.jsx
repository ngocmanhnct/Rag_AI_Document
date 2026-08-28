import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { streamChat } from '../api/chat';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const query = input.trim();
    if (!query || streaming) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: query }, { role: 'assistant', content: '' }]);
    setStreaming(true);

    try {
      await streamChat(query, (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updated[updated.length - 1].content + token,
          };
          return updated;
        });
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: 'assistant', content: 'Đã có lỗi xảy ra, vui lòng thử lại.' };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper flex flex-col">
      <header className="flex justify-between items-center px-8 py-6 border-b border-ink/20">
        <div>
          <p className="font-mono text-[10px] tracking-widest text-ink-light uppercase">Phòng tra cứu</p>
          <h1 className="font-display text-2xl text-ink">Hỏi đáp tài liệu</h1>
        </div>
        <Link to="/" className="font-mono text-xs text-ink underline">← Kho tài liệu</Link>
      </header>

      <main className="flex-1 overflow-y-auto px-8 py-6 space-y-4 max-w-3xl w-full mx-auto">
        {messages.length === 0 && (
          <p className="font-body text-ink-light italic">Đặt câu hỏi về tài liệu đã tải lên...</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={
                m.role === 'user'
                  ? 'bg-ink text-paper font-body px-4 py-2.5 max-w-[80%] rounded-sm'
                  : 'bg-card border border-ink/30 text-ink font-body px-4 py-2.5 max-w-[80%] rounded-sm'
              }
            >
              {m.content || (streaming && i === messages.length - 1 ? '···' : '')}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </main>

      <form onSubmit={handleSend} className="border-t border-ink/20 p-4 max-w-3xl w-full mx-auto flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Nhập câu hỏi..."
          className="flex-1 border border-ink/30 bg-card px-3 py-2 font-body text-ink focus:outline-none focus:border-ink focus:ring-1 focus:ring-ink"
        />
        <button
          type="submit"
          disabled={streaming}
          className="bg-ink text-paper font-display px-5 py-2 hover:opacity-90 transition disabled:opacity-50"
        >
          Hỏi
        </button>
      </form>
    </div>
  );
}