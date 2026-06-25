"use client";

import { CornerRightUp, FileUp, Paperclip, X } from "lucide-react";
import { useRef, useState } from "react";
import { useFileInput } from "@/app/components/hooks/use-file-input";
import { useAutoResizeTextarea } from "@/app/components/hooks/use-auto-resize-textarea";

interface FileDisplayProps {
  fileName: string;
  onClear: () => void;
}

function FileDisplay({ fileName, onClear }: FileDisplayProps) {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "4px 12px",
        borderRadius: "var(--radius-md)",
        background: "var(--color-surface-2)",
        border: "1px solid var(--color-border)",
        fontSize: 12,
        color: "var(--color-text-secondary)",
        marginBottom: 6,
      }}
    >
      <FileUp size={14} color="var(--color-text-muted)" />
      <span style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {fileName}
      </span>
      <button
        type="button"
        onClick={onClear}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 2,
          borderRadius: "50%",
          border: "none",
          background: "none",
          cursor: "pointer",
          color: "var(--color-text-muted)",
          lineHeight: 1,
        }}
        title="Remove file"
      >
        <X size={12} />
      </button>
    </div>
  );
}

interface AIInputWithFileProps {
  id?: string;
  placeholder?: string;
  minHeight?: number;
  maxHeight?: number;
  accept?: string;
  maxFileSize?: number;
  onSubmit?: (message: string, file?: File) => void;
  className?: string;
}

export function AIInputWithFile({
  id = "ai-input-with-file",
  placeholder = "Ask anything or upload context (max 5MB)…",
  minHeight = 52,
  maxHeight = 200,
  accept = "image/*,application/pdf,text/plain",
  maxFileSize = 5,
  onSubmit,
}: AIInputWithFileProps) {
  const [inputValue, setInputValue] = useState<string>("");
  const [hoverAttach, setHoverAttach] = useState(false);
  const [hoverSend, setHoverSend] = useState(false);

  const { fileName, fileInputRef, handleFileSelect, clearFile, selectedFile } =
    useFileInput({ accept, maxSize: maxFileSize });

  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight,
    maxHeight,
  });

  const handleSubmit = () => {
    if (inputValue.trim() || selectedFile) {
      onSubmit?.(inputValue, selectedFile ?? undefined);
      setInputValue("");
      clearFile();
      adjustHeight(true);
    }
  };

  const canSend = inputValue.trim().length > 0 || !!selectedFile;

  return (
    <div style={{ width: "100%", maxWidth: 800, margin: "0 auto" }}>
      {/* File pill */}
      {fileName && <FileDisplay fileName={fileName} onClear={clearFile} />}

      {/* Input wrapper */}
      <div
        style={{
          position: "relative",
          borderRadius: "var(--radius-lg)",
          border: "1px solid var(--color-border)",
          background: "var(--color-surface)",
          boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
          transition: "border-color var(--transition-fast), box-shadow var(--transition-fast)",
        }}
        onFocus={() => {}}
      >
        {/* Paperclip button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          onMouseEnter={() => setHoverAttach(true)}
          onMouseLeave={() => setHoverAttach(false)}
          title="Attach file"
          style={{
            position: "absolute",
            left: 12,
            top: "50%",
            transform: "translateY(-50%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 30,
            height: 30,
            borderRadius: "var(--radius-md)",
            border: "none",
            background: hoverAttach ? "var(--color-surface-2)" : "transparent",
            color: hoverAttach ? "var(--color-text)" : "var(--color-text-muted)",
            cursor: "pointer",
            transition: "all var(--transition-fast)",
          }}
        >
          <Paperclip size={15} style={{ transform: "rotate(45deg) scaleX(-1)" }} />
        </button>

        {/* Hidden native file input — display:none ensures browser UI is NEVER shown */}
        <input
          type="file"
          style={{ display: "none" }}
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept={accept}
        />

        {/* Textarea */}
        <textarea
          id={id}
          ref={textareaRef}
          value={inputValue}
          placeholder={placeholder}
          onChange={e => {
            setInputValue(e.target.value);
            adjustHeight();
          }}
          onKeyDown={e => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          style={{
            width: "100%",
            paddingLeft: 50,
            paddingRight: 52,
            paddingTop: 14,
            paddingBottom: 14,
            minHeight: minHeight,
            maxHeight: maxHeight,
            background: "transparent",
            border: "none",
            outline: "none",
            resize: "none",
            color: "var(--color-text)",
            fontSize: 14,
            fontFamily: "var(--font-sans)",
            lineHeight: 1.5,
            overflowY: "auto",
            display: "block",
            boxSizing: "border-box",
          }}
        />

        {/* Send button */}
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canSend}
          onMouseEnter={() => setHoverSend(true)}
          onMouseLeave={() => setHoverSend(false)}
          title="Send"
          style={{
            position: "absolute",
            right: 10,
            top: "50%",
            transform: "translateY(-50%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 34,
            height: 34,
            borderRadius: "var(--radius-md)",
            border: "none",
            background: canSend
              ? hoverSend
                ? "var(--color-primary-hover)"
                : "var(--color-primary)"
              : "var(--color-surface-2)",
            color: canSend ? "#fff" : "var(--color-text-muted)",
            cursor: canSend ? "pointer" : "not-allowed",
            opacity: canSend ? 1 : 0.5,
            transition: "all var(--transition-fast)",
            boxShadow: canSend ? "0 0 12px rgba(99,102,241,0.3)" : "none",
          }}
        >
          <CornerRightUp size={15} />
        </button>
      </div>

      {/* Hint text */}
      <div style={{
        fontSize: 11,
        color: "var(--color-text-muted)",
        marginTop: 6,
        paddingLeft: 2,
      }}>
        Press <kbd style={{
          fontSize: 10,
          fontFamily: "var(--font-mono)",
          padding: "1px 5px",
          borderRadius: 4,
          background: "var(--color-surface-2)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-muted)",
        }}>Enter</kbd> to send · <kbd style={{
          fontSize: 10,
          fontFamily: "var(--font-mono)",
          padding: "1px 5px",
          borderRadius: 4,
          background: "var(--color-surface-2)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-muted)",
        }}>Shift+Enter</kbd> for new line
      </div>
    </div>
  );
}
