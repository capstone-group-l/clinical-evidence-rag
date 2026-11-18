import { Navigate } from "react-router-dom";
import { useAuth } from "./auth-context";

export default function RequireAuth({ children }) {
  const { session, loading } = useAuth();

  if (loading) return null;
  if (!session) return <Navigate to="/login" replace />;
  return children;
}
