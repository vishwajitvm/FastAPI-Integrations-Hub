import { useLocation } from "react-router-dom";
import { useState } from "react";

const Home = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);

  const name = queryParams.get("name") ?? "Guest";
  const email = queryParams.get("email") ?? "Unknown";
  const sub = queryParams.get("sub") ?? "";
//   const accessToken = queryParams.get("access_token") ?? "";
//   const refreshToken = queryParams.get("refresh_token") ?? "";

  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/Chat/ask?user_id=${sub}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ query }),
      });

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.answer || "No response received." },
      ]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: "⚠️ Error: Could not get response." }]);
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white flex flex-col items-center justify-center px-4">
      {/* User Info */}
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-yellow-400">👋 Welcome, {name}</h1>
        <p className="text-sm text-yellow-100">Email: {email}</p>
        <p className="text-sm text-yellow-100">User ID: {sub}</p>
      </div>

      {/* Chatbot Box */}
      <div className="bg-[#2a2a2a] shadow-xl shadow-yellow-300/20 rounded-2xl p-6 w-full max-w-6xl text-center">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-yellow-400">🤖 Bee Logical Chatbot</h2>
          <p className="text-sm text-yellow-100 mt-1">Ask your question below</p>
        </div>

        {/* Chat Display */}
        <div className="bg-gray-900 p-4 mb-4 h-64 overflow-y-auto rounded-lg text-left space-y-3">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-2 rounded-md max-w-4xl ${
                msg.role === "user"
                  ? "bg-yellow-600 ml-auto text-right"
                  : "bg-gray-700 text-left"
              }`}
            >
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="text-yellow-200 text-sm italic">Bot is typing...</div>
          )}
        </div>

        {/* Chat Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            name="query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
            placeholder="Ask something..."
            className="px-4 py-2 rounded-md bg-[#1f1f1f] border border-yellow-400 text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
          <button
            type="submit"
            className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition"
            disabled={loading}
          >
            {loading ? "Asking..." : "Ask"}
          </button>
        </form>

        {/* Action Buttons */}
        <div className="mt-6 space-y-2 text-sm text-yellow-200">
          <a
            href={`http://localhost:8000/folders/my-folder-and-files-n8n?user_id=${sub}`}
            className="block hover:text-yellow-400"
          >
            📂 List My Folders & Files
          </a>
          <a
            href={`http://localhost:8000/folders/my-teams-folder-and-files?user_id=${sub}`}
            className="block hover:text-yellow-400"
          >
            👥 List Team Folders & Files
          </a>
          <a
            href="http://localhost:8000/get-access-token"
            className="block hover:text-yellow-400"
          >
            🔐 Get Access Token
          </a>
          <a
            href={`http://localhost:8000/api/user-access-token?user_id=${sub}`}
            className="block hover:text-yellow-400"
          >
            🔑 Get API USER Access Token
          </a>
          <a
            href="http://localhost:8000/get-user-id"
            className="block hover:text-yellow-400"
          >
            🆔 Get User ID
          </a>
          <a
            href="http://localhost:8000/logout"
            className="block text-red-400 hover:text-red-500 font-semibold"
          >
            🚪 Logout
          </a>
        </div>
      </div>
    </div>
  );
};

export default Home;
