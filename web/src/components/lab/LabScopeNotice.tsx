import Link from "next/link";
import { CAPABILITIES } from "@/content/science-copy";
import styles from "./LabScopeNotice.module.css";

const LAB = CAPABILITIES.find((c) => c.id === "lab");

/**
 * A slim line above every Lab stage. It says what kind of model this is, that it runs in the
 * browser, and that saved runs stay in this browser (Phase 0 decision 2). The comparison with the
 * Python run is stated exactly, from the reviewed capability text.
 */
export function LabScopeNotice() {
  return (
    <aside className={styles.notice} aria-label="What the Lab is">
      <p className={styles.line}>
        <strong>Kinematic model. No muscle or wing physics. Output is model state.</strong>{" "}
        Runs in your browser. Saved runs stay in this browser.
      </p>
      <details className={styles.more}>
        <summary>How exact is it?</summary>
        <p>{LAB?.reason}</p>
        <p><Link href="/science/status">What is and is not established</Link></p>
      </details>
    </aside>
  );
}
