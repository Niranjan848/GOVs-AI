import { useState, useCallback } from 'react';
import type { Profile, ProfileCompletion } from '../types';
import { profileAPI } from '../lib/api';

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [completion, setCompletion] = useState<ProfileCompletion | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    try {
      const { data } = await profileAPI.get();
      setProfile(data as Profile);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (updates: Partial<Profile>) => {
    try {
      const { data } = await profileAPI.update(updates);
      setProfile(data as Profile);
      return true;
    } catch (error) {
      console.error('Failed to update profile:', error);
      return false;
    }
  }, []);

  const fetchCompletion = useCallback(async () => {
    try {
      const { data } = await profileAPI.getCompletion();
      setCompletion(data as ProfileCompletion);
    } catch (error) {
      console.error('Failed to fetch completion:', error);
    }
  }, []);

  return {
    profile,
    completion,
    isLoading,
    fetchProfile,
    updateProfile,
    fetchCompletion,
  };
}
