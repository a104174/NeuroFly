import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./DataTable.module.css";

export interface Column<T> {
  readonly id: string;
  readonly label: string;
  /** Sortable columns render a link that sets the sort in the URL. */
  readonly sortable?: boolean;
  readonly render: (row: T) => ReactNode;
}
export type SortDirection = "asc" | "desc";

/**
 * A real table: caption, scoped headers, aria-sort on the sorted column. Below 600 px each row
 * becomes a stacked block with its column label, and explicit roles keep the table semantics.
 */
export function DataTable<T>({ caption, columns, rows, rowKey, rowHeader, sort, sortHref }: {
  caption: string;
  columns: readonly Column<T>[];
  rows: readonly T[];
  rowKey: (row: T) => string;
  /** The column whose cells are row headers. */
  rowHeader: string;
  sort?: { id: string; direction: SortDirection };
  sortHref?: (id: string, direction: SortDirection) => string;
}) {
  return (
    <div className={styles.wrap}>
      <table className={styles.table} role="table">
        <caption>{caption}</caption>
        <thead>
          <tr role="row">
            {columns.map((column) => {
              const active = sort?.id === column.id;
              const next: SortDirection = active && sort?.direction === "asc" ? "desc" : "asc";
              return (
                <th key={column.id} scope="col" role="columnheader" aria-sort={active ? (sort!.direction === "asc" ? "ascending" : "descending") : column.sortable ? "none" : undefined}>
                  {column.sortable && sortHref ? (
                    <Link prefetch={false} scroll={false} href={sortHref(column.id, next)} className={styles.sort}>
                      {column.label}<span aria-hidden="true" className={styles.arrow}>{active ? (sort!.direction === "asc" ? "↑" : "↓") : ""}</span>
                    </Link>
                  ) : column.label}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)} role="row">
              {columns.map((column) => column.id === rowHeader ? (
                <th key={column.id} scope="row" role="rowheader" data-label={column.label}>{column.render(row)}</th>
              ) : (
                <td key={column.id} role="cell" data-label={column.label}>{column.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
