export function StateMessage({
  eyebrow,
  title,
  detail,
  tone = "neutral",
}: {
  eyebrow: string;
  title: string;
  detail: string;
  tone?: "neutral" | "error";
}) {
  return (
    <section className={`state-message state-message-${tone}`} role={tone === "error" ? "alert" : undefined}>
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p className="state-detail">{detail}</p>
    </section>
  );
}
