import Link from "next/link";
import { LAB_CLAIMS, type LabTool } from "./labClaims";
import styles from "./LabScopeNotice.module.css";

export function LabScopeNotice({ tool }: { tool: LabTool }) {
  const c = LAB_CLAIMS[tool];
  return (
    <aside className={styles.notice} aria-label="What this tool is">
      <p className={styles.line}><strong>{c.line}</strong></p>
      <details className={styles.more}>
        <summary>What is this based on?</summary>
        {c.proof.map((text) => <p key={text}>{text}</p>)}
        <p>Evidence in the repository:</p>
        <ul>{c.paths.map((path) => <li key={path}><code>{path}</code></li>)}</ul>
        <p><Link href="/science/status">What is and is not established</Link></p>
      </details>
    </aside>
  );
}
