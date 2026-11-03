import Link from "next/link";
import { KindGlyph } from "@/components/ui";
import { STATUS_HREF } from "./siteContent";
import styles from "./SiteChrome.module.css";

/**
 * Present on every page, so no route can look more certain than the project is. It states
 * the two facts that hold everywhere: this is a model, and it is not evaluated against real flies.
 */
export function StatusPill() {
  return (
    <Link prefetch={false} href={STATUS_HREF} className={styles.pill} aria-label="Model · Not evaluated. Status and limits">
      <KindGlyph kind="not-evaluated" size={12} />
      <span>Model · Not evaluated</span>
    </Link>
  );
}
