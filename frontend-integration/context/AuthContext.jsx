/**
 * AuthContext — provides auth state and actions to the entire React app.
 *
 * Cross-tab sync strategy:
 *   - On mount: fetch fresh profile from server (not just localStorage)
 *   - storage event: fires in ALL OTHER tabs when localStorage changes —
 *     we listen for "user" key changes and update React state immediately
 *   - visibilitychange event: when a hidden tab becomes visible again,
 *     re-fetch profile from server to catch any updates made in other tabs
 *
 * Usage:
 *   1. Wrap your app in <AuthProvider>
 *   2. Use the hook anywhere:  const { user, login, logout, updateProfile } = useAuth()
 */

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  getProfile,
  updateProfile as apiUpdateProfile,
  uploadAvatar as apiUploadAvatar,
  removeAvatar as apiRemoveAvatar,
  getCurrentUser,
  isAuthenticated,
} from "../api/authService";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser]       = useState(getCurrentUser());
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  // ---------------------------------------------------------------------------
  // On mount: fetch fresh profile from server so every tab starts with
  // up-to-date data (avatar, name, etc.) regardless of localStorage state.
  // ---------------------------------------------------------------------------
  useEffect(() => {
    if (isAuthenticated()) {
      getProfile()
        .then((freshUser) => setUser(freshUser))
        .catch(() => setUser(null));
    }
  }, []);

  // ---------------------------------------------------------------------------
  // Cross-tab sync via storage event.
  //
  // The storage event fires in every tab EXCEPT the one that made the change.
  // So when Tab A updates the profile and writes to localStorage["user"],
  // Tab B and Tab C receive this event and update their React state instantly.
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === "user") {
        if (event.newValue) {
          // Another tab updated the user (profile change, login, register)
          try {
            setUser(JSON.parse(event.newValue));
          } catch {
            // Malformed JSON — ignore
          }
        } else {
          // Another tab cleared the user (logout)
          setUser(null);
        }
      }

      if (event.key === "access_token" && !event.newValue) {
        // Another tab logged out — clear this tab too
        setUser(null);
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  // ---------------------------------------------------------------------------
  // Visibility sync: when the user switches back to this tab after being away,
  // re-fetch the profile from the server to pick up any changes made elsewhere.
  // This covers the case where the storage event was missed (e.g. native apps,
  // PWA, or the tab was in a background process group).
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && isAuthenticated()) {
        getProfile()
          .then((freshUser) => setUser(freshUser))
          .catch(() => {
            // Token expired — clear state
            setUser(null);
          });
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiLogin(credentials);
      // Login response contains full profile with absolute avatar URL
      setUser(data.user);
      return data;
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        "Login failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRegister(formData);
      setUser(data.user);
      return data;
    } catch (err) {
      const msg =
        err.response?.data?.email?.[0] ||
        err.response?.data?.password?.[0] ||
        err.response?.data?.detail ||
        "Registration failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
    // clearTokens() in apiLogout already removes localStorage["user"],
    // which triggers the storage event in other tabs automatically.
  };

  /**
   * Update profile fields (including avatar file upload).
   * Syncs React state + localStorage so all other tabs pick it up via
   * the storage event.
   *
   * @param {{ first_name?, last_name?, bio?, avatar?: File }} data
   * @returns {Promise<UserProfile>} Full updated profile with absolute avatar URL
   */
  const updateProfile = useCallback(async (data) => {
    setLoading(true);
    setError(null);
    try {
      const updatedUser = await apiUpdateProfile(data);
      // apiUpdateProfile already writes to localStorage["user"],
      // which fires the storage event in all other tabs.
      setUser(updatedUser);
      return updatedUser;
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.avatar?.[0] ||
        "Profile update failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Upload or replace avatar image.
   * @param {File} file
   */
  const uploadAvatar = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    try {
      const updatedUser = await apiUploadAvatar(file);
      setUser(updatedUser);
      return updatedUser;
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.avatar?.[0] ||
        "Avatar upload failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Remove avatar — deletes file from disk and clears DB field.
   * Returns updated profile with avatar: null.
   */
  const removeAvatar = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const updatedUser = await apiRemoveAvatar();
      setUser(updatedUser);
      return updatedUser;
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        "Avatar removal failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        login,
        register,
        logout,
        updateProfile,
        uploadAvatar,
        removeAvatar,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
};
