import { useEffect, useState } from "react";
import { AuthContext } from "./auth-context";
import { supabase } from "./supabase";

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const { data } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      setLoading(false);
    });
    return () => data.subscription.unsubscribe();
  }, []);

  const value = { session, loading };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
