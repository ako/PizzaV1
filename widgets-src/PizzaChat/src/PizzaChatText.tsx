import { CSSProperties, ReactElement, useMemo, useRef } from "react";
import MarkdownIt from "markdown-it";
import { PizzaChatTextContainerProps } from "../typings/PizzaChatTextProps";
import { splitMessage } from "./components/segments";
import { CardView } from "./components/Cards";
import { sendToChat } from "./components/chatInput";
import "./ui/PizzaChatText.css";

// A chat message of the pizza assistant: markdown (raw HTML escaped, as the
// Markdown viewer it replaces in Conversational UI), ```card blocks as cards whose
// facts come from the app, and ```suggestions as follow-up chips. After
// ako/ChatV2's ChatRichText.

const md = new MarkdownIt("default", { html: false, linkify: true, typographer: true });

export function PizzaChatText(props: PizzaChatTextContainerProps): ReactElement | null {
    const { stringAttribute, class: className, style } = props as PizzaChatTextContainerProps & { class?: string; style?: CSSProperties };
    const value = stringAttribute.status === "available" ? stringAttribute.value ?? "" : "";
    const segments = useMemo(() => splitMessage(value), [value]);
    const root = useRef<HTMLDivElement>(null);
    if (stringAttribute.status !== "available") return null;
    return (
        <div ref={root} className={`widget-markdown pc-root ${className ?? ""}`} style={style}>
            {segments.map((s, i) => {
                if (s.kind === "markdown") return <div key={i} className="pc-md" dangerouslySetInnerHTML={{ __html: md.render(s.text) }} />;
                if (s.kind === "pending") return <div key={i} className="pc-card pc-pending" aria-busy="true">Preparing a card…</div>;
                if (s.kind === "suggestions") {
                    return (
                        <div key={i} className="pc-suggest" role="group" aria-label="Suggested questions">
                            {s.items.map((q, j) => <button type="button" key={j} className="pc-chip" onClick={() => sendToChat(q, root.current)}>{q}</button>)}
                        </div>
                    );
                }
                return <div key={i} className="pc-cards">{s.cards.map((c, j) => <CardView key={j} card={c} />)}</div>;
            })}
        </div>
    );
}
