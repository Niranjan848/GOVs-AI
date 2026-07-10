import { useState, useCallback } from 'react';
import type { Message, ChatListItem } from '../types';
import { chatAPI } from '../lib/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatId, setChatId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<ChatListItem[]>([]);

  const sendMessage = useCallback(async (content: string) => {
    // Add user message optimistically
    const tempUserMsg: Message = {
      id: Date.now(),
      chat_id: chatId || 0,
      role: 'user',
      content,
      metadata_json: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const { data } = await chatAPI.send(content, chatId || undefined);
      const aiMsg = data as Message;
      setChatId(aiMsg.chat_id);
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: Date.now() + 1,
        chat_id: chatId || 0,
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please make sure the backend server is running and try again.',
        metadata_json: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [chatId]);

  const loadChat = useCallback(async (id: number) => {
    try {
      const { data } = await chatAPI.getChat(id);
      setChatId(id);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const { data } = await chatAPI.getHistory();
      setHistory(data as ChatListItem[]);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  }, []);

  const startNewChat = useCallback(() => {
    setChatId(null);
    setMessages([]);
  }, []);

  return {
    messages,
    chatId,
    isLoading,
    history,
    sendMessage,
    loadChat,
    loadHistory,
    startNewChat,
  };
}
