"use client";

import { useEffect } from "react";
import { PageShell } from "@/components/site/PageShell";
import { ButtonLink, StatePanel } from "@/components/ui";
import { STATE_COPY } from "@/content/science-copy";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <PageShell title="Something went wrong">
      <StatePanel
        state="route-error"
        reference={error.digest}
        actions={
          <>
            <button type="button" onClick={() => reset()} style={{ minBlockSize: "var(--button-height-md)", paddingInline: "var(--space-4)", border: 0, borderRadius: "var(--radius-md)", background: "var(--color-accent)", color: "var(--color-on-accent)", font: "inherit", fontWeight: 600, cursor: "pointer" }}>{STATE_COPY.routeError.retry}</button>
            <ButtonLink variant="quiet" href="/">{STATE_COPY.routeError.home}</ButtonLink>
          </>
        }
      />
    </PageShell>
  );
}
