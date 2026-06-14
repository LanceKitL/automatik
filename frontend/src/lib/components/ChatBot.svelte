<script lang="ts">
	import { untrack } from 'svelte';
	import { X, Send, Bot } from '@lucide/svelte';
	import { sendChatbotMessage } from '$lib/services/api';
	import { marked } from 'marked';

	marked.setOptions({ breaks: true, gfm: true });

	let { open = $bindable(false), toggle = 0, enabled = true } = $props();

	type Msg = { role: 'user' | 'bot'; text: string };
	let messages = $state<Msg[]>([]);
	let input = $state('');
	let typing = $state(false);
	let chatEl = $state<HTMLDivElement | null>(null);
	let started = $state(false);

	// When `open` flips to true, show the window.
	// When user clicks X, set minimized (bubble still shows).
	// When user clicks bubble, go back to window.
	// When user clicks X on bubble, close entirely.
	let minimized = $state(false);

	function scrollBottom() {
		requestAnimationFrame(() => {
			if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
		});
	}

	function addMessage(role: 'user' | 'bot', text: string) {
		messages = [...messages, { role, text }];
		scrollBottom();
	}

	async function handleSend() {
		const q = input.trim();
		if (!q || typing) return;
		addMessage('user', q);
		input = '';
		typing = true;
		scrollBottom();
		try {
			const history = messages.map((m) => ({ role: m.role, text: m.text }));
			const res = await sendChatbotMessage({ message: q, history });
			typing = false;
			addMessage('bot', res.response);
		} catch {
			typing = false;
			addMessage('bot', 'I\'m having trouble connecting right now. Please try again or contact us at **info@automatik.com**.');
		}
	}

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSend();
		}
	}

	function ensureStarted() {
		if (!started) {
			started = true;
			addMessage('bot', 'Hi! I\'m **AutoBot** 🤖 Ask me anything about our vehicles, financing, services, or anything dealership-related!');
		}
		scrollBottom();
	}

	function openWindow() {
		open = true;
		minimized = false;
		ensureStarted();
	}

	function minimizeWindow() {
		minimized = true;
	}

	function closeAll() {
		open = false;
		minimized = false;
	}

	// Navbar button toggle: open→minimize→window cycle
	function handleNavToggle() {
		if (!open) {
			openWindow();
		} else if (minimized) {
			minimized = false;
			ensureStarted();
		} else {
			minimizeWindow();
		}
	}

	$effect(() => {
		if (open) {
			if (!enabled) {
				open = false;
				return;
			}
			ensureStarted();
		}
	});

	// Navbar button toggle signal
	$effect(() => {
		if (toggle > 0) {
			untrack(() => {
				if (!open) {
					open = true;
					minimized = false;
					ensureStarted();
				} else if (minimized) {
					minimized = false;
					ensureStarted();
				} else {
					minimized = true;
				}
			});
		}
	});
</script>

<div class="chat-fab">
	{#if open && !minimized}
		<div class="chat-window" role="dialog" aria-modal="true">
			<div class="chat-header">
				<div class="chat-header-left">
					<Bot size={20} />
					<div>
						<span class="chat-title">AutoBot</span>
						<span class="chat-status">Online</span>
					</div>
				</div>
				<div class="chat-header-actions">
					<button class="chat-header-btn" onclick={minimizeWindow} aria-label="Minimize">—</button>
					<button class="chat-header-btn" onclick={closeAll} aria-label="Close"><X size={16} /></button>
				</div>
			</div>

			<div class="chat-messages" bind:this={chatEl}>
				{#each messages as msg, i}
					<div class="msg-row" class:user-msg={msg.role === 'user'} class:bot-msg={msg.role === 'bot'}>
						<div class="msg-bubble">
							{#if msg.role === 'bot'}
								<Bot size={14} class="msg-avatar" />
							{/if}
							<div class="msg-text">{@html marked.parse(msg.text)}</div>
						</div>
					</div>
				{/each}
				{#if typing}
					<div class="msg-row bot-msg">
						<div class="msg-bubble typing-bubble">
							<Bot size={14} class="msg-avatar" />
							<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>
						</div>
					</div>
				{/if}
			</div>

			<div class="chat-input-row">
				<input class="chat-input" type="text" bind:value={input} onkeydown={handleKey} placeholder="Ask me anything…" disabled={typing} />
				<button class="chat-send" onclick={handleSend} disabled={!input.trim() || typing}><Send size={16} /></button>
			</div>
		</div>
	{:else if open && minimized}
		<button class="chat-bubble" onclick={openWindow} aria-label="Open AutoBot">
			<Bot size={24} />
		</button>
	{/if}
</div>

<style>
	.chat-fab { position: fixed; bottom: 24px; right: 24px; z-index: 1010; }

	.chat-bubble {
		width: 56px; height: 56px; border-radius: 50%; border: none;
		background: #1a1a2e; color: #e8c97e; cursor: pointer;
		display: flex; align-items: center; justify-content: center;
		box-shadow: 0 4px 20px rgba(0,0,0,0.2);
		transition: transform 0.2s, box-shadow 0.2s;
	}
	.chat-bubble:hover { transform: scale(1.1); box-shadow: 0 6px 28px rgba(0,0,0,0.25); }

	.chat-window {
		width: 380px; max-width: calc(100vw - 48px);
		height: 520px; max-height: calc(100vh - 120px);
		background: #fff; border-radius: 16px;
		box-shadow: 0 8px 40px rgba(0,0,0,0.15);
		display: flex; flex-direction: column; overflow: hidden;
		animation: slideUp 0.25s ease-out;
	}
	@keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }

	.chat-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-bottom: 1px solid #e5e7eb; background: #1a1a2e; color: #fff; flex-shrink: 0; }
	.chat-header-left { display: flex; align-items: center; gap: 10px; }
	.chat-header-left :global(svg) { color: #e8c97e; }
	.chat-title { font-size: 14px; font-weight: 700; display: block; }
	.chat-status { font-size: 10px; color: #34d399; display: block; }
	.chat-header-actions { display: flex; gap: 4px; }
	.chat-header-btn { background: none; border: none; color: rgba(255,255,255,0.6); cursor: pointer; padding: 2px 6px; border-radius: 4px; font-size: 16px; line-height: 1; display: flex; align-items: center; }
	.chat-header-btn:hover { color: #fff; background: rgba(255,255,255,0.1); }

	.chat-messages { flex: 1; overflow-y: auto; padding: 14px 16px; display: flex; flex-direction: column; gap: 8px; }
	.chat-messages::-webkit-scrollbar { width: 4px; }
	.chat-messages::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }

	.msg-row { display: flex; }
	.user-msg { justify-content: flex-end; }
	.bot-msg { justify-content: flex-start; }
	.msg-bubble { max-width: 85%; padding: 9px 13px; border-radius: 14px; font-size: 13px; line-height: 1.5; display: flex; gap: 6px; align-items: flex-start; animation: fadeIn 0.2s ease-out; }
	@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
	.user-msg .msg-bubble { background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
	.bot-msg .msg-bubble { background: #f3f4f6; color: #1f2937; border-bottom-left-radius: 4px; }
	.msg-avatar { flex-shrink: 0; margin-top: 2px; color: #6b7280; }
	.bot-msg .msg-avatar { color: var(--primary); }
	.msg-text { word-break: break-word; line-height: 1.5; }
	.msg-text :global(a) { color: var(--primary); text-decoration: underline; }
	.msg-text :global(strong) { font-weight: 600; }
	.msg-text :global(p) { margin: 0 0 6px; }
	.msg-text :global(p:last-child) { margin-bottom: 0; }
	.msg-text :global(ul), .msg-text :global(ol) { margin: 4px 0; padding-left: 18px; }
	.msg-text :global(li) { margin-bottom: 2px; }
	.msg-text :global(code) { background: #f3f4f6; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
	.user-msg .msg-text :global(a) { color: #bfdbfe; }
	.user-msg .msg-text :global(code) { background: rgba(255,255,255,0.15); color: #fff; }
	.user-msg .msg-text :global(p) { color: #fff; }
	.user-msg .msg-text :global(ul), .user-msg .msg-text :global(ol) { color: #fff; }
	.user-msg .msg-text :global(li) { color: #fff; }

	.typing-bubble { padding: 12px 16px; }
	.typing-dots span { animation: dotPulse 1.2s infinite; font-size: 20px; line-height: 1; color: #6b7280; }
	.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
	.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
	@keyframes dotPulse { 0%, 60%, 100% { opacity: 0.3; } 30% { opacity: 1; } }

	.chat-input-row { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-top: 1px solid #e5e7eb; flex-shrink: 0; }
	.chat-input { flex: 1; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 24px; font-family: var(--font-sans); font-size: 13px; outline: none; }
	.chat-input:focus { border-color: var(--primary); }
	.chat-send { width: 36px; height: 36px; border-radius: 50%; border: none; background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; transition: background 0.2s; }
	.chat-send:hover:not(:disabled) { background: var(--primary-dark); }
	.chat-send:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
