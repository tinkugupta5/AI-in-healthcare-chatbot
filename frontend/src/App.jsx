import { useState } from 'react'
import { ThinkingOrb } from 'thinking-orbs'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [error, setError] = useState('')

  async function askQuestion(event) {
    event.preventDefault()
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion || isThinking) return
    setQuestion('')
    setError('')
    setMessages((current) => [...current, { role: 'user', content: trimmedQuestion }])
    setIsThinking(true)
    try {
      const response = await fetch('http://localhost:8000/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: trimmedQuestion }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'The reference could not answer.')
      setMessages((current) => [...current, { role: 'assistant', content: data.answer, sources: data.sources }])
    } catch (requestError) { setError(requestError.message) } finally { setIsThinking(false) }
  }

  return <main className="app-shell">
    <header className="topbar"><div className="brand-mark">M</div><div><p className="eyebrow">Private reference assistant</p><h1>Medibot</h1></div><div className="status"><span /> Reference ready</div></header>
    <section className="workspace">
      <aside className="intro-panel"><div className="orb-stage"><ThinkingOrb state={isThinking ? 'searching' : 'listening'} size={64} /></div><p className="eyebrow">Medical knowledge base</p><h2>Clear answers from your reference library.</h2><p className="muted">Ask about symptoms, conditions, or terminology. Every answer is grounded in the indexed medical encyclopedia.</p><div className="safety-note"><span>i</span><p>For educational use only. This does not replace professional medical advice.</p></div></aside>
      <section className="chat-panel"><div className="chat-header"><div><p className="eyebrow">Conversation</p><h2>Ask your question</h2></div><span className="model-label">Llama 3.1 · FAISS</span></div><div className="messages" aria-live="polite">
        {messages.length === 0 && <div className="empty-state"><div className="empty-icon">+</div><p>What would you like to understand?</p><span>Try “What is fever?”</span></div>}
        {messages.map((message, index) => <article className={`message ${message.role}`} key={`${message.role}-${index}`}><span className="message-label">{message.role === 'user' ? 'You' : 'Medibot'}</span><p>{message.content}</p>{message.sources?.length > 0 && <small>Sources: {message.sources.map((source) => `p. ${source.page}`).join(', ')}</small>}</article>)}
        {isThinking && <div className="thinking-row"><ThinkingOrb state="searching" size={20} /><span>Searching the reference...</span></div>}
      </div>{error && <p className="error">{error}</p>}<form className="composer" onSubmit={askQuestion}><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a medical question..." aria-label="Medical question" /><button type="submit" disabled={isThinking || !question.trim()} aria-label="Send question">↗</button></form></section>
    </section>
  </main>
}

export default App
