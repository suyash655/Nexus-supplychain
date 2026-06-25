/**
 * Safe markdown-like text renderer.
 * Converts **bold** to <strong> and splits by newline for paragraphs.
 * Returns an array of React elements — NO dangerouslySetInnerHTML.
 */
export function SafeMarkdown({ text }: { text: string }) {
  if (!text) return null;

  const lines = text.split("\n");

  return (
    <>
      {lines.map((line, i) => {
        // Convert **bold** to strong elements
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
          <span key={i}>
            {parts.map((part, j) => {
              if (part.startsWith("**") && part.endsWith("**")) {
                return <strong key={j}>{part.slice(2, -2)}</strong>;
              }
              // Convert - bullet to •
              if (part.startsWith("- ")) {
                return <span key={j}>• {part.slice(2)}</span>;
              }
              return <span key={j}>{part}</span>;
            })}
            {i < lines.length - 1 && <br />}
          </span>
        );
      })}
    </>
  );
}
