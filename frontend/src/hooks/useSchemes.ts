import { useState, useCallback, useEffect } from 'react';
import type { Scheme, Bookmark } from '../types';
import { schemeAPI } from '../lib/api';

export function useSchemes() {
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSchemes = useCallback(async (params?: { category?: string; search?: string }) => {
    setIsLoading(true);
    try {
      const { data } = await schemeAPI.list(params);
      setSchemes(data as Scheme[]);
    } catch (error) {
      console.error('Failed to fetch schemes:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchBookmarks = useCallback(async () => {
    try {
      const { data } = await schemeAPI.getBookmarks();
      setBookmarks(data as Bookmark[]);
    } catch (error) {
      console.error('Failed to fetch bookmarks:', error);
    }
  }, []);

  const toggleBookmark = useCallback(async (schemeId: number) => {
    const isBookmarked = bookmarks.some((b) => b.scheme.id === schemeId);
    try {
      if (isBookmarked) {
        await schemeAPI.removeBookmark(schemeId);
        setBookmarks((prev) => prev.filter((b) => b.scheme.id !== schemeId));
      } else {
        const { data } = await schemeAPI.bookmark(schemeId);
        setBookmarks((prev) => [...prev, data as Bookmark]);
      }
    } catch (error) {
      console.error('Bookmark toggle failed:', error);
    }
  }, [bookmarks]);

  const isBookmarked = useCallback(
    (schemeId: number) => bookmarks.some((b) => b.scheme.id === schemeId),
    [bookmarks]
  );

  return {
    schemes,
    bookmarks,
    isLoading,
    fetchSchemes,
    fetchBookmarks,
    toggleBookmark,
    isBookmarked,
  };
}
