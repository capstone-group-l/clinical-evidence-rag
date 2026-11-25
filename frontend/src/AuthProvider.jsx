import { useEffect, useState } from "react";
import { AuthContext } from "./auth-context";
import { getMe } from "./api";
import { supabase } from "./supabase";

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState(null);

  useEffect(() => {
    const { data } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      setLoading(false);
      if (newSession) {
        getMe(newSession.access_token)
          .then((me) => {
            if (me) {
              setRole(me.role);
            } else {
              setRole(null);
            }
          })
          .catch(() => setRole(null));
      } else {
        setRole(null);
      }
    });
    return () => data.subscription.unsubscribe();
  }, []);

  const value = { session, loading, role };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
