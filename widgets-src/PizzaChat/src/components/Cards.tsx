import { ReactElement, ReactNode, useEffect, useState } from "react";
import { Card, CardAction } from "./segments";
import { ActionResult, CartInfo, getJson, OrderInfo, openPage, postJson, ProductInfo, ZoneInfo } from "./appApi";
import { MiniMap } from "./MiniMap";

// The pizza chat's cards. Each card names something; its facts come from the app
// (rest/pizzachat/v1) with the guest's own session. Buttons run fixed actions:
// "add" posts to the app, the others open a shop page.

const LABEL: Record<string, string> = { products: "Menu", cart: "Cart", zone: "Delivery", order: "Order", info: "Info" };

type Load<T> = { state: "loading" } | { state: "ready"; data: T } | { state: "failed"; message: string };

function useApi<T>(path: string | undefined, refresh = 0): Load<T> {
    const [load, setLoad] = useState<Load<T>>({ state: "loading" });
    useEffect(() => {
        if (!path) return;
        let live = true;
        setLoad(l => (l.state === "ready" ? l : { state: "loading" }));
        getJson<T>(path).then(data => live && setLoad({ state: "ready", data })).catch((e: Error) => live && setLoad({ state: "failed", message: e.message }));
        return () => { live = false; };
    }, [path, refresh]);
    return load;
}

function Shell({ card, eyebrow, status, tone, children }: { card: Card; eyebrow?: string; status?: string; tone?: string; children?: ReactNode }): ReactElement {
    return (
        <article className={`pc-card pc-tone-${tone ?? card.tone} pc-type-${card.type}`} aria-label={`${eyebrow ?? LABEL[card.type]} ${card.title}`}>
            <header className="pc-card-head">
                <div className="pc-card-heading">
                    <span className="pc-eyebrow">{eyebrow ?? LABEL[card.type]}</span>
                    {card.title && <span className="pc-title">{card.title}</span>}
                    {card.subtitle && <span className="pc-subtitle">{card.subtitle}</span>}
                </div>
                {status && <span className="pc-status">{status}</span>}
            </header>
            {children}
            {card.note && <p className="pc-note">{card.note}</p>}
            {card.actions.length > 0 && <Actions actions={card.actions} />}
        </article>
    );
}

function Loading({ what }: { what: string }): ReactElement {
    return <p className="pc-muted" aria-busy="true">Loading {what}…</p>;
}

// ------------------------------------------------------------ actions
function AddButton({ code, quantity = 1, label }: { code: string; quantity?: number; label: string }): ReactElement {
    const [busy, setBusy] = useState(false);
    const [result, setResult] = useState<ActionResult | null>(null);
    const add = (): void => {
        setBusy(true);
        postJson<ActionResult>("rest/pizzachat/v1/actions", { action: "add", code, quantity })
            .then(setResult)
            .catch((e: Error) => setResult({ ok: false, message: e.message }))
            .finally(() => setBusy(false));
    };
    return (
        <span className="pc-add">
            <button type="button" className="pc-btn pc-btn-primary" onClick={add} disabled={busy} aria-busy={busy}>
                <span className="ms" aria-hidden="true">add_shopping_cart</span>{busy ? "Adding…" : label}
            </button>
            {result && <span className={`pc-result ${result.ok ? "pc-ok" : "pc-bad"}`} role="status">{result.message}</span>}
        </span>
    );
}

function TrackButton({ order, label }: { order: string; label: string }): ReactElement {
    const [message, setMessage] = useState<string | undefined>();
    const open = (): void => {
        getJson<OrderInfo>(`rest/pizzachat/v1/order?number=${encodeURIComponent(order)}`)
            .then(o => (o.found && o.trackUrl ? openPage(o.trackUrl) : setMessage("This order cannot be opened here.")))
            .catch((e: Error) => setMessage(e.message));
    };
    return (
        <span className="pc-add">
            <button type="button" className="pc-btn" onClick={open}><span className="ms" aria-hidden="true">local_shipping</span>{label}</button>
            {message && <span className="pc-result pc-bad" role="status">{message}</span>}
        </span>
    );
}

function Actions({ actions }: { actions: CardAction[] }): ReactElement {
    return (
        <div className="pc-actions">
            {actions.map((a, i) => {
                if (a.action === "add" && a.code) return <AddButton key={i} code={a.code} quantity={a.quantity} label={a.label} />;
                if (a.action === "track" && a.order) return <TrackButton key={i} order={a.order} label={a.label} />;
                const path = a.action === "checkout" ? "p/checkout" : "p/menu";
                return <button key={i} type="button" className="pc-btn" onClick={() => openPage(path)}>
                    <span className="ms" aria-hidden="true">{a.action === "checkout" ? "shopping_cart_checkout" : "restaurant_menu"}</span>{a.label}
                </button>;
            })}
        </div>
    );
}

// ------------------------------------------------------------ card types
function ProductsCard({ card }: { card: Card }): ReactElement {
    const load = useApi<{ products?: ProductInfo[] }>(`rest/pizzachat/v1/products?codes=${encodeURIComponent(card.codes.join(","))}`);
    return (
        <Shell card={card}>
            {load.state === "loading" && <Loading what="the menu" />}
            {load.state === "failed" && <p className="pc-muted">The menu could not be loaded: {load.message}</p>}
            {load.state === "ready" && (
                <ul className="pc-products">
                    {(load.data.products ?? []).map(p => (
                        <li key={p.code} className={`pc-product${p.orderable ? "" : " pc-soldout"}`}>
                            {p.image && <img className="pc-product-img" src={p.image} alt={p.imageAlt ?? p.name} loading="lazy" />}
                            <div className="pc-product-body">
                                <div className="pc-product-top">
                                    <span className="pc-product-name">{p.name}</span>
                                    {p.price && <span className="pc-price">{p.price}</span>}
                                </div>
                                {p.subtitle && <span className="pc-product-sub">{p.subtitle}</span>}
                                <span className="pc-tags">
                                    {p.diet && <span className={`pc-tag pc-tag-${p.diet}`}>{p.diet}</span>}
                                    {p.spice && <span className="pc-tag pc-tag-spicy">{p.spice}</span>}
                                    {!p.orderable && <span className="pc-tag pc-tag-out">sold out</span>}
                                </span>
                                {p.allergens && <span className="pc-allergens">Allergens: {p.allergens}</span>}
                                {p.orderable && <AddButton code={p.code} label="Add to cart" />}
                            </div>
                        </li>
                    ))}
                    {(load.data.products ?? []).length === 0 && <li className="pc-muted">Not on the menu.</li>}
                </ul>
            )}
        </Shell>
    );
}

function CartCard({ card }: { card: Card }): ReactElement {
    const [refresh, setRefresh] = useState(0);
    const load = useApi<CartInfo>("rest/pizzachat/v1/cart", refresh);
    const cart = load.state === "ready" ? load.data : undefined;
    return (
        <Shell card={card} status={cart ? `${cart.count} item${cart.count === 1 ? "" : "s"}` : undefined}>
            {load.state === "loading" && <Loading what="your cart" />}
            {load.state === "failed" && <p className="pc-muted">The cart could not be loaded: {load.message}</p>}
            {cart && (cart.lines ?? []).length === 0 && <p className="pc-muted">Your cart is empty.</p>}
            {cart && (cart.lines ?? []).length > 0 && (
                <>
                    <ul className="pc-lines">
                        {(cart.lines ?? []).map((l, i) => (
                            <li key={i} className={l.available === false ? "pc-unavailable" : undefined}>
                                <span className="pc-qty">{l.quantity}×</span>
                                <span className="pc-line-name">{l.name}{l.detail && <span className="pc-line-detail">{l.detail}</span>}</span>
                                <span className="pc-amount">{l.amount}</span>
                            </li>
                        ))}
                    </ul>
                    <dl className="pc-fields">
                        <div className="pc-field"><dt>Subtotal</dt><dd>{cart.subtotal}</dd></div>
                        {cart.coupon && <div className="pc-field"><dt>Coupon</dt><dd>{cart.coupon}</dd></div>}
                    </dl>
                    {cart.block && <p className="pc-note pc-warn">{cart.block}</p>}
                    <div className="pc-actions">
                        <button type="button" className="pc-btn pc-btn-primary" disabled={!cart.canCheckout} onClick={() => openPage("p/checkout")}>
                            <span className="ms" aria-hidden="true">shopping_cart_checkout</span>Checkout
                        </button>
                        <button type="button" className="pc-btn" onClick={() => setRefresh(r => r + 1)}><span className="ms" aria-hidden="true">refresh</span>Refresh</button>
                    </div>
                </>
            )}
        </Shell>
    );
}

function ZoneCard({ card }: { card: Card }): ReactElement {
    const load = useApi<ZoneInfo>(`rest/pizzachat/v1/zone?zip=${encodeURIComponent(card.zip ?? "")}`);
    const z = load.state === "ready" ? load.data : undefined;
    return (
        <Shell card={{ ...card, title: card.title || `ZIP ${card.zip}` }} status={z ? (z.ok ? "in the zone" : "outside the zone") : undefined} tone={z ? (z.ok ? "good" : "warning") : undefined}>
            {load.state === "loading" && <Loading what="the delivery zone" />}
            {load.state === "failed" && <p className="pc-muted">The delivery zone could not be loaded: {load.message}</p>}
            {z && (
                <>
                    <MiniMap store={[z.storeLat, z.storeLon]} dest={z.ok ? [z.destLat, z.destLon] : undefined} destLabel={z.ok ? z.neighborhood : undefined} distance={z.ok ? z.distance : undefined} />
                    <p className="pc-note">{z.message}</p>
                </>
            )}
        </Shell>
    );
}

function OrderCard({ card }: { card: Card }): ReactElement {
    const [refresh, setRefresh] = useState(0);
    const load = useApi<OrderInfo>(`rest/pizzachat/v1/order?number=${encodeURIComponent(card.order ?? "")}`, refresh);
    const o = load.state === "ready" ? load.data : undefined;
    // live while the order is moving: refresh every 10 s until it is done
    const moving = !!o?.found && o.tone === "info";
    useEffect(() => {
        if (!moving) return;
        const t = window.setInterval(() => setRefresh(r => r + 1), 10000);
        return () => window.clearInterval(t);
    }, [moving]);
    if (o && !o.found) {
        return <Shell card={{ ...card, title: card.title || `MX-${card.order}` }}><p className="pc-muted">This order is not one of yours in this session. Ask the assistant to find it with the order number and the email used at checkout.</p></Shell>;
    }
    return (
        <Shell card={{ ...card, title: o?.number ?? (card.title || `MX-${card.order}`), subtitle: o ? `${o.items} · ${o.total} · ${o.address}` : card.subtitle }}
            status={o?.statusPlain} tone={o?.tone}>
            {load.state === "loading" && <Loading what="the order" />}
            {load.state === "failed" && <p className="pc-muted">The order could not be loaded: {load.message}</p>}
            {o && o.delivery && <MiniMap store={[o.storeLat, o.storeLon]} dest={[o.destLat, o.destLon]} destLabel={o.address} distance={o.distance} courier={o.courier} />}
            {o && (o.events ?? []).length > 0 && (
                <ol className="pc-timeline">
                    {(o.events ?? []).map((e, i) => (
                        <li key={i} className={i === (o.events ?? []).length - 1 ? "pc-latest" : undefined}><time>{e.at}</time><span>{e.text}</span></li>
                    ))}
                </ol>
            )}
            {o?.trackUrl && card.actions.length === 0 && (
                <div className="pc-actions">
                    <button type="button" className="pc-btn" onClick={() => openPage(o.trackUrl as string)}><span className="ms" aria-hidden="true">local_shipping</span>Open tracking</button>
                </div>
            )}
        </Shell>
    );
}

function InfoCard({ card }: { card: Card }): ReactElement {
    return (
        <Shell card={card}>
            {card.fields.length > 0 && (
                <dl className="pc-fields">
                    {card.fields.map((f, i) => <div className="pc-field" key={i}><dt>{f.label}</dt><dd>{f.value}</dd></div>)}
                </dl>
            )}
            {card.items.length > 0 && (
                <ul className="pc-items">
                    {card.items.map((it, i) => (
                        <li key={i}><span className="pc-item-title">{it.title}</span>{it.text && <span className="pc-item-text">{it.text}</span>}{it.value && <span className="pc-item-value">{it.value}</span>}</li>
                    ))}
                </ul>
            )}
        </Shell>
    );
}

export function CardView({ card }: { card: Card }): ReactElement {
    switch (card.type) {
        case "products": return <ProductsCard card={card} />;
        case "cart": return <CartCard card={card} />;
        case "zone": return <ZoneCard card={card} />;
        case "order": return <OrderCard card={card} />;
        default: return <InfoCard card={card} />;
    }
}
