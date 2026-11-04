import type { Metadata } from "next";
import { PageShell } from "@/components/site/PageShell";
import { Card, KindBadge } from "@/components/ui";

export const metadata: Metadata = {
  title: "Lab · NeuroFly",
  description: "Three interactive tools: the Explore arena, the research tools and the fly viewer. Explore and the research tools run model code in your browser.",
};

/** Every statement below comes from existing descriptions of these tools; none is new. */
const TOOLS = [
  {
    href: "/visual-lab/arena",
    title: "Explore",
    models: "Simulated walking and flight in a 3D enclosure. Movement follows engineering rules, with a neural steering influence from a selected circuit.",
    leaves: "No muscle or wing physics, no calibrated vision, and no biological gait.",
    kind: "model-assumption" as const,
  },
  {
    href: "/visual-lab/arena/research",
    title: "Research tools",
    models: "Historical modes, controlled experiments and integrity-checked replays, with more detailed controls and instrumentation.",
    leaves: "The same limits as Explore. Larger screens work best.",
    kind: "model-state" as const,
  },
  {
    href: "/visual-lab/fly",
    title: "Fly viewer",
    models: "An interactive look at the male Drosophila visual asset, with its body parts.",
    leaves: "It is not a scientific simulation, and it is not reconstructed MaleCNS anatomy.",
    kind: "unavailable" as const,
  },
];

export default function LabOverviewPage() {
  return (
    <>
      <PageShell
        eyebrow="Lab"
        title="The Lab"
        current="/visual-lab"
        lead={<p>Three tools for exploring the model. Explore and the research tools run model code in your browser; the fly viewer only shows a body model. Each tool says what it is based on.</p>}
      >
        <ul style={{ display: "grid", gap: "var(--space-5)", margin: "var(--space-6) 0 0", padding: 0, listStyle: "none", gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 20rem), 1fr))" }}>
          {TOOLS.map((tool) => (
            <li key={tool.href}>
              <Card eyebrow="Lab tool" title={tool.title} href={tool.href} variant="interactive" meta={[{ label: "Kind", value: <KindBadge kind={tool.kind} /> }]}>
                <p><strong>What it models.</strong> {tool.models}</p>
                <p><strong>What it leaves out.</strong> {tool.leaves}</p>
              </Card>
            </li>
          ))}
        </ul>
      </PageShell>
    </>
  );
}
