import { cn } from "@/lib/utils";
import { SourceCitation } from "./source-citation";
import type { Message } from "@/types/conversation";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn("flex", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3",
          isUser
            ? "bg-primary text-white"
            : "bg-white border border-slate-200"
        )}
      >
        <p
          className={cn(
            "text-sm whitespace-pre-wrap",
            isStreaming && !isUser && "streaming-cursor"
          )}
        >
          {message.content}
        </p>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-1">
            <p className="text-xs font-medium text-muted-foreground mb-1">
              Sources
            </p>
            {message.sources.map((source, i) => (
              <SourceCitation key={i} source={source} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
