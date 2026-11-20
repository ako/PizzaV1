// Splits a chat message into markdown, card and suggestion segments.
//
// A card block is a fenced code block whose info string is `card` (one card)
// or `cards` (a JSON array of cards):
//
//   ```card
//   {"type":"products","codes":["PZ-01","PZ-07"],"title":"Two vegetarian picks"}
//   ```
//
// Pizza cards carry NAMES, never facts: a products card names product codes, an
// order card an order number, a zone card a ZIP code. The widget asks the app for
// the facts (rest/pizzachat/v1), so a model cannot put a made-up price, status or
// position in front of a guest. The content is data, never markup: every value is
// rendered as text. While a message streams in, a card block that has opened but
// not yet closed is reported as "pending".

export type Tone = "neutral" | "good" | "warning" | "critical" | "info";
export type CardType = "products" | "cart" | "zone" | "order" | "info";

export interface CardField { label: string; value: string }
export interface CardItem { title: string; text?: string; value?: string }

/** A button on a card. The app runs a fixed action with the guest's own session. */
export type ActionKind = "add" | "checkout" | "track" | "menu";
export interface CardAction { label: string; action: ActionKind; code?: string; order?: string; quantity?: number }

export interface Card {
    type: CardType;
    title: string;
    subtitle?: string;
    tone: Tone;
    codes: string[];
    zip?: string;
    order?: string;
    fields: CardField[];
    items: CardItem[];
    note?: string;
    actions: CardAction[];
}

export type Segment =
    | { kind: "markdown"; text: string }
    | { kind: "cards"; cards: Card[] }
    | { kind: "suggestions"; items: string[] }
    | { kind: "pending" };

const TONES: Tone[] = ["neutral", "good", "warning", "critical", "info"];
const TYPES: CardType[] = ["products", "cart", "zone", "order", "info"];
const FENCE = /^(`{3,}|~{3,})[ \t]*(card|cards)[ \t]*$/i;
const SUGGEST = /^(`{3,}|~{3,})[ \t]*suggestions[ \t]*$/i;
const MAX_SUGGESTIONS = 4;
const MAX_CODES = 6;

function str(v: unknown): string | undefined {
    if (v === null || v === undefined) return undefined;
    if (typeof v === "string") return v.trim() === "" ? undefined : v;
    if (typeof v === "number" || typeof v === "boolean") return String(v);
    return undefined;
}

function list<T>(v: unknown, map: (x: unknown) => T | undefined): T[] {
    if (!Array.isArray(v)) return [];
    const out: T[] = [];
    for (const x of v) {
        const m = map(x);
        if (m !== undefined) out.push(m);
    }
    return out;
}

/** A product code as the menu has them (e.g. PZ-01, DR-03): letters, digits and - only. */
export function cleanCode(v: unknown): string | undefined {
    const s = str(v)?.trim().toUpperCase();
    return s && /^[A-Z0-9][A-Z0-9-]{0,7}$/.test(s) ? s : undefined;
}

/** An order number as the app shows it: 1061 or MX-1061. Returned as digits. */
export function cleanOrder(v: unknown): string | undefined {
    const m = /^(?:MX-?)?(\d{1,8})$/i.exec(str(v)?.trim() ?? "");
    return m ? m[1] : undefined;
}

/** A US ZIP code: five digits. */
export function cleanZip(v: unknown): string | undefined {
    const s = str(v)?.trim();
    return s && /^\d{5}$/.test(s) ? s : undefined;
}

function toAction(a: unknown): CardAction | undefined {
    if (!a || typeof a !== "object") return undefined;
    const r = a as Record<string, unknown>;
    const action = (str(r.action) ?? "").toLowerCase();
    const label = str(r.label)?.slice(0, 40);
    if (!label) return undefined;
    if (action === "add") {
        const code = cleanCode(r.code);
        const q = Number(r.quantity ?? 1);
        return code ? { label, action, code, quantity: Number.isInteger(q) && q >= 1 && q <= 10 ? q : 1 } : undefined;
    }
    if (action === "track") {
        const order = cleanOrder(r.order ?? r.ref);
        return order ? { label, action, order } : undefined;
    }
    if (action === "checkout" || action === "menu") return { label, action };
    return undefined;
}

/** Turns one parsed JSON value into a Card, or undefined when it has nothing to show. */
export function toCard(raw: unknown): Card | undefined {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return undefined;
    const o = raw as Record<string, unknown>;
    const typeRaw = (str(o.type) ?? "info").toLowerCase();
    const type: CardType = typeRaw === "product" ? "products" : (TYPES as string[]).includes(typeRaw) ? (typeRaw as CardType) : "info";
    const toneRaw = (str(o.tone) ?? "neutral").toLowerCase();
    const codes = [...new Set(list(Array.isArray(o.codes) ? o.codes : [o.code], cleanCode))].slice(0, MAX_CODES);
    const card: Card = {
        type,
        title: str(o.title)?.slice(0, 80) ?? "",
        subtitle: str(o.subtitle)?.slice(0, 120),
        tone: (TONES as string[]).includes(toneRaw) ? (toneRaw as Tone) : "neutral",
        codes,
        zip: cleanZip(o.zip),
        order: cleanOrder(o.order ?? o.ref),
        fields: list(o.fields, f => {
            if (!f || typeof f !== "object") return undefined;
            const r = f as Record<string, unknown>;
            const label = str(r.label), value = str(r.value);
            return label !== undefined && value !== undefined ? { label: label.slice(0, 40), value: value.slice(0, 200) } : undefined;
        }).slice(0, 12),
        items: list(o.items, i => {
            if (typeof i === "string") return { title: i.slice(0, 120) };
            if (!i || typeof i !== "object") return undefined;
            const r = i as Record<string, unknown>;
            const title = str(r.title);
            return title !== undefined ? { title: title.slice(0, 120), text: str(r.text)?.slice(0, 200), value: str(r.value)?.slice(0, 40) } : undefined;
        }).slice(0, 12),
        note: str(o.note)?.slice(0, 300),
        actions: list(o.actions, toAction).slice(0, 3)
    };
    if (card.type === "products" && !card.codes.length) return undefined;
    if (card.type === "zone" && !card.zip) return undefined;
    if (card.type === "order" && !card.order) return undefined;
    if (card.type === "info" && !card.title && !card.fields.length && !card.items.length && !card.note) return undefined;
    return card;
}

export function splitMessage(content: string): Segment[] {
    const lines = (content ?? "").split("\n");
    const out: Segment[] = [];
    let md: string[] = [];
    const flushMd = (): void => {
        const text = md.join("\n");
        if (text.trim() !== "") out.push({ kind: "markdown", text });
        md = [];
    };
    for (let i = 0; i < lines.length; i++) {
        const sug = SUGGEST.exec(lines[i].trim());
        if (sug) {
            let j = i + 1;
            const body: string[] = [];
            while (j < lines.length && !lines[j].trim().startsWith(sug[1].slice(0, 3))) { body.push(lines[j]); j++; }
            flushMd();
            if (j >= lines.length) return out;   // still streaming: show them once complete
            try {
                const parsed: unknown = JSON.parse(body.join("\n"));
                const items = list(parsed, s => { const v = str(s)?.trim(); return v && v.length <= 120 ? v : undefined; }).slice(0, MAX_SUGGESTIONS);
                if (items.length) out.push({ kind: "suggestions", items });
            } catch { /* not a list: leave it out */ }
            i = j;
            continue;
        }
        const open = FENCE.exec(lines[i].trim());
        if (!open) { md.push(lines[i]); continue; }
        const fence = open[1];
        const plural = open[2].toLowerCase() === "cards";
        let j = i + 1;
        const body: string[] = [];
        while (j < lines.length && !lines[j].trim().startsWith(fence.slice(0, 3))) { body.push(lines[j]); j++; }
        if (j >= lines.length) { flushMd(); out.push({ kind: "pending" }); return out; }
        let cards: Card[] = [];
        try {
            const parsed: unknown = JSON.parse(body.join("\n"));
            const arr = plural || Array.isArray(parsed) ? (Array.isArray(parsed) ? parsed : [parsed]) : [parsed];
            cards = list(arr, toCard);
        } catch { cards = []; }
        if (cards.length) { flushMd(); out.push({ kind: "cards", cards }); }
        // not valid card data: left out rather than shown to a guest as raw JSON
        i = j;
    }
    flushMd();
    return out;
}
