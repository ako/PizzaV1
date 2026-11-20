// Calls to the app's own REST service (rest/pizzachat/v1) with the guest's
// session: the CSRF token Mendix requires on a session-authenticated call. URLs
// are built from the app's root, so they work from any page (/p/menu, /p/track/…).

type Mx = { appUrl?: string; session?: { getConfig?: (k: string) => unknown; sessionData?: { csrftoken?: string } } };
const mx = (): Mx | undefined => (window as unknown as { mx?: Mx }).mx;

/** The app's root URL, ending in "/". */
export function appUrl(path: string): string {
    const root = mx()?.appUrl ?? "/";
    return (root.endsWith("/") ? root : root + "/") + path.replace(/^\//, "");
}

function csrfToken(): string | undefined {
    const fromConfig = mx()?.session?.getConfig?.("csrftoken");
    return typeof fromConfig === "string" ? fromConfig : mx()?.session?.sessionData?.csrftoken;
}

function headers(json: boolean): Record<string, string> {
    const h: Record<string, string> = { Accept: "application/json" };
    if (json) h["Content-Type"] = "application/json";
    const token = csrfToken();
    if (token) h["X-Csrf-Token"] = token;
    return h;
}

export async function getJson<T>(path: string): Promise<T> {
    const r = await fetch(appUrl(path), { headers: headers(false), credentials: "same-origin" });
    if (!r.ok) throw new Error(`The app answered ${r.status}.`);
    return r.json() as Promise<T>;
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
    const r = await fetch(appUrl(path), { method: "POST", headers: headers(true), credentials: "same-origin", body: JSON.stringify(body) });
    if (!r.ok) throw new Error(`The app answered ${r.status}.`);
    return r.json() as Promise<T>;
}

/** Opens one of the shop's pages (checkout, menu, a tracking link). */
export function openPage(path: string): void {
    window.location.assign(appUrl(path));
}

// ------------------------------------------------------------ API shapes
export interface ProductInfo { code: string; name: string; subtitle?: string; kind?: string; price?: string; image?: string; imageAlt?: string; diet?: string; spice?: string; allergens?: string; orderable?: boolean }
export interface CartInfo { count: number; subtotal?: string; total?: string; coupon?: string; block?: string; canCheckout?: boolean; lines?: Array<{ name: string; detail?: string; quantity: number; amount?: string; available?: boolean }> }
export interface ZoneInfo { zip: string; ok: boolean; neighborhood?: string; distance?: string; message?: string; storeLat: number; storeLon: number; destLat: number; destLon: number }
export interface OrderInfo { found: boolean; number?: string; status?: string; statusPlain?: string; tone?: string; delivery?: boolean; address?: string; items?: string; total?: string; distance?: string; trackUrl?: string; storeLat: number; storeLon: number; destLat: number; destLon: number; courier: number; events?: Array<{ at: string; text: string }> }
export interface ActionResult { ok: boolean; message?: string; count?: number }
