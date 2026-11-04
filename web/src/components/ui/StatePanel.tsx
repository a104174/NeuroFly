import type { ReactNode } from "react";
import { STATE_COPY } from "@/content/science-copy";
import styles from "./StatePanel.module.css";

type Common = {
  /** Heading level, so the panel fits the page's outline. */
  headingLevel?: 2 | 3;
  className?: string;
};
/**
 * Every error and empty state names what happened and what still works (brief section 5).
 * Recovery controls are passed as `actions` so they stay real links and buttons.
 */
export type StatePanelProps = Common &
  (
    | { state: "loading"; /** For example "313 neuron shapes". */ what: string }
    | { state: "empty"; message: string; actions?: ReactNode }
    | { state: "api-down"; actions?: ReactNode }
    /** The service answered, but the stored data failed its hash or reconstruction checks. */
    | { state: "integrity-failure"; actions?: ReactNode }
    | { state: "route-error"; /** Error digest or request reference. */ reference?: string; actions?: ReactNode }
    | { state: "not-found"; /** Links to the main sections. */ links?: ReactNode }
    | { state: "unknown-id"; noun: string; id: string; actions?: ReactNode }
    | { state: "webgl-off"; /** True only when a data table or list shows the same information. */ hasDataAlternative: boolean; actions?: ReactNode }
    | { state: "context-lost"; actions?: ReactNode }
    /** The data is not installed on this deployment. Not an outage: retrying will not help. */
    | { state: "not-on-deployment"; actions?: ReactNode }
    | { state: "low-power"; actions?: ReactNode }
    | { state: "missing-data"; /** For example "Neuron shapes". */ what: string; detail?: string }
  );

export function StatePanel(props: StatePanelProps) {
  const { headingLevel = 2, className } = props;
  const Heading = `h${headingLevel}` as "h2" | "h3";
  let title: ReactNode, body: ReactNode = null, actions: ReactNode = null;
  let role: "alert" | "status" | undefined, tone: "error" | "neutral" = "neutral";

  switch (props.state) {
    case "loading":
      role = "status"; title = STATE_COPY.loading3d(props.what); break;
    case "empty":
      title = props.message; actions = props.actions; break;
    case "api-down":
      role = "alert"; tone = "error"; title = STATE_COPY.apiDown.title; body = STATE_COPY.apiDown.body; actions = props.actions; break;
    case "integrity-failure":
      role = "alert"; tone = "error"; title = STATE_COPY.integrityFailure.title; body = STATE_COPY.integrityFailure.body; actions = props.actions; break;
    case "route-error":
      role = "alert"; tone = "error"; title = STATE_COPY.routeError.title; actions = props.actions;
      body = props.reference ? <>{STATE_COPY.routeError.reference}: <code>{props.reference}</code></> : null; break;
    case "not-found":
      title = STATE_COPY.notFound.title; body = STATE_COPY.notFound.body; actions = props.links; break;
    case "unknown-id":
      title = <>{STATE_COPY.unknownId.before(props.noun)} <code>{props.id}</code>{STATE_COPY.unknownId.after}</>; actions = props.actions; break;
    case "webgl-off":
      title = STATE_COPY.webglOff.title; body = props.hasDataAlternative ? STATE_COPY.webglOff.withData : null; actions = props.actions; break;
    case "not-on-deployment":
      role = "status"; title = STATE_COPY.notOnDeployment.title; body = STATE_COPY.notOnDeployment.body; actions = props.actions; break;
    case "context-lost":
      role = "alert"; title = STATE_COPY.contextLost.title; body = STATE_COPY.contextLost.body; actions = props.actions; break;
    case "low-power":
      title = STATE_COPY.lowPower.title; actions = props.actions; break;
    case "missing-data":
      title = STATE_COPY.missing(props.what); body = props.detail ?? null; break;
  }

  return (
    <section
      className={`${styles.panel} ${className ?? ""}`}
      data-state={props.state}
      data-tone={tone}
      role={role}
      aria-busy={props.state === "loading" || undefined}
    >
      {props.state === "loading" ? <span className={styles.bar} aria-hidden="true" /> : null}
      <Heading className={styles.title}>{title}</Heading>
      {body ? <p className={styles.body}>{body}</p> : null}
      {actions ? <div className={styles.actions}>{actions}</div> : null}
    </section>
  );
}
