import Link from "next/link";
import styles from "./SegmentedLinks.module.css";

export interface SegmentedItem { readonly id: string; readonly label: string; readonly href: string; readonly current: boolean }

/**
 * A filter whose state lives in the URL. Each option is a real link, so it works without
 * JavaScript, can be shared and survives a reload. The selected option has aria-current="true".
 */
export function SegmentedLinks({ label, items }: { label: string; items: readonly SegmentedItem[] }) {
  return (
    <div role="group" aria-label={label} className={styles.group}>
      {items.map((item) => (
        <Link key={item.id} prefetch={false} href={item.href} scroll={false} aria-current={item.current ? "true" : undefined} className={styles.item}>{item.label}</Link>
      ))}
    </div>
  );
}
