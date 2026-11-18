import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "./auth-context";
import { supabase } from "./supabase";

const MIN_PASSWORD_LENGTH = 6;

function loginErrorMessage(error) {
  if (error.code === "email_not_confirmed") {
    return "Please confirm your email first. Check your inbox.";
  }
  if (error.code === "invalid_credentials" || error.status === 400) {
    return "Wrong email or password.";
  }
  return "Could not sign in right now. Please try again.";
}

function signupErrorMessage(error) {
  if (error.code === "weak_password") {
    return error.message;
  }
  return "Could not create the account. Please try again.";
}

export default function LoginPage() {
  const { session, loading } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);
  const isSignup = mode === "signup";

  if (!loading && session) return <Navigate to="/" replace />;

  function switchMode() {
    setMode(isSignup ? "login" : "signup");
    setPassword("");
    setConfirmPassword("");
    setError(null);
    setInfo(null);
  }

  async function handleLogin() {
    const { error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    if (error) {
      setError(loginErrorMessage(error));
      return;
    }
    navigate("/", { replace: true });
  }

  async function handleSignup() {
    const displayName = name.trim();
    if (!displayName) {
      setError("Please enter your name.");
      return;
    }
    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(
        `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`,
      );
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    const { error } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: {
        emailRedirectTo: window.location.origin,
        data: { display_name: displayName },
      },
    });
    if (error) {
      setError(signupErrorMessage(error));
      return;
    }
    setPassword("");
    setConfirmPassword("");
    setInfo("Check your email to confirm your account.");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setInfo(null);
    setSubmitting(true);
    try {
      await (isSignup ? handleSignup() : handleLogin());
    } catch {
      setError(
        isSignup
          ? "Could not create the account. Please try again."
          : "Could not sign in right now. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  let buttonLabel = isSignup ? "Sign up" : "Log in";
  if (submitting) {
    buttonLabel = isSignup ? "Creating account..." : "Logging in...";
  }

  return (
    <main>
      <h1>Clinical Evidence RAG</h1>
      <div className="intro">
        <p>
          {isSignup
            ? "Create an account to ask clinical questions."
            : "Log in to ask clinical questions."}
        </p>
      </div>

      <form className="query-form" onSubmit={handleSubmit}>
        {isSignup && (
          <>
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              autoComplete="name"
              required
              value={name}
              readOnly={submitting}
              onChange={(e) => setName(e.target.value)}
            />
          </>
        )}

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          readOnly={submitting}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          autoComplete={isSignup ? "new-password" : "current-password"}
          required
          value={password}
          readOnly={submitting}
          onChange={(e) => setPassword(e.target.value)}
        />

        {isSignup && (
          <>
            <label htmlFor="confirm-password">Confirm password</label>
            <input
              id="confirm-password"
              type="password"
              autoComplete="new-password"
              required
              value={confirmPassword}
              readOnly={submitting}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </>
        )}

        <div className="form-footer">
          <button type="button" className="link-button" onClick={switchMode}>
            {isSignup ? "Have an account? Log in" : "No account? Sign up"}
          </button>
          <button type="submit" className="ask-button" disabled={submitting}>
            {submitting && <span className="spinner" />}
            {buttonLabel}
          </button>
        </div>
      </form>

      {error && (
        <div className="status status-error" role="alert">
          <p>{error}</p>
        </div>
      )}

      {info && (
        <div className="status status-info" role="status">
          <p>{info}</p>
        </div>
      )}
    </main>
  );
}
