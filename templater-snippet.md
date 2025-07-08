```javascript
<%*
const question = await tp.system.prompt("Ask your vault assistant:");
if (!question) return "";

const folder = "Career Roadmap"; // Change this to your target folder

tR += `⏳ Searching your vault for “${question}”…\n\n`;

try {
  const resp = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: question, folder })
  });
  if (!resp.ok) throw new Error(`${resp.status}: ${await resp.text()}`);
  const { response } = await resp.json();
  tR += `## Assistant Response\n\n${response}\n\n---`;
} catch (e) {
  tR += `❌ Error: ${e.message}\n\nEnsure your AI server is running.`;
}
%>
```