# How to integrate this backend with your React/Vite project

## 1. Copy files into your React project

```
frontend-integration/
  api/              → copy to  src/api/
  context/          → copy to  src/context/
```

## 2. Install axios

```bash
npm install axios
```

## 3. Wrap your app with AuthProvider

Edit `src/main.jsx`:

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
```

## 4. Set up protected routes (React Router v6)

```jsx
// src/App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./context/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected — must be logged in */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/projects"  element={<Projects />} />
          <Route path="/orders"    element={<Orders />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

## 5. Use auth in any component

```jsx
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav>
      <span>Hello, {user?.first_name}</span>
      <button onClick={logout}>Logout</button>
    </nav>
  );
}
```

## 6. Login page example

```jsx
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(form);
      navigate("/dashboard");
    } catch (_) {
      // error is already set in context
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
      />
      <input
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
```

## 7. Register page example

```jsx
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "", first_name: "", last_name: "",
    password: "", password2: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(form);
      navigate("/dashboard");
    } catch (_) {}
  };

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="First name"       onChange={set("first_name")} />
      <input placeholder="Last name"        onChange={set("last_name")} />
      <input type="email" placeholder="Email"    onChange={set("email")} />
      <input type="password" placeholder="Password"  onChange={set("password")} />
      <input type="password" placeholder="Confirm"   onChange={set("password2")} />
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Creating account..." : "Register"}
      </button>
    </form>
  );
}
```

## 8. Fetch protected data example

```jsx
import { useEffect, useState } from "react";
import { getProjects } from "../api/projectsService";

export default function Projects() {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    getProjects().then(setProjects);
  }, []);

  return (
    <ul>
      {projects.results?.map((p) => (
        <li key={p.id}>{p.title} — {p.status}</li>
      ))}
    </ul>
  );
}
```

---

## API Quick Reference

| Action | Code |
|--------|------|
| Login | `const { login } = useAuth(); await login({ email, password })` |
| Register | `const { register } = useAuth(); await register({ email, first_name, last_name, password, password2 })` |
| Logout | `const { logout } = useAuth(); await logout()` |
| Get profile | `import { getProfile } from "../api/authService"; await getProfile()` |
| List projects | `import { getProjects } from "../api/projectsService"; await getProjects()` |
| Create project | `import { createProject } from "../api/projectsService"; await createProject({ title, description })` |
| List orders | `import { getOrders } from "../api/ordersService"; await getOrders()` |

---

## Admin Panel

URL: http://127.0.0.1:8000/admin/
Email: admin@webxter.com
Password: Admin@1234
