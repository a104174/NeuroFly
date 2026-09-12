import { AppHeader } from "@/components/AppHeader";
import { StateMessage } from "@/components/StateMessage";

export default function NotFound() {
  return (
    <div className="app-shell">
      <AppHeader />
      <main className="main-content main-content-wide">
        <StateMessage
          eyebrow="EXPERIMENT NOT FOUND"
          title="That artifact is unavailable."
          detail="Choose a completed run from the catalogue instead."
          tone="error"
        />
      </main>
    </div>
  );
}
