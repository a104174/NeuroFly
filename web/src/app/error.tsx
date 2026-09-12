"use client";

import { useEffect } from "react";

import { AppHeader } from "@/components/AppHeader";
import { StateMessage } from "@/components/StateMessage";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="app-shell">
      <AppHeader />
      <main className="main-content main-content-wide">
        <StateMessage
          eyebrow="REQUEST ERROR"
          title="This view could not load."
          detail="The persisted experiment response was unavailable or invalid. Try the request again."
          tone="error"
        />
        <button className="retry-button" type="button" onClick={() => reset()}>
          Retry request
        </button>
      </main>
    </div>
  );
}
