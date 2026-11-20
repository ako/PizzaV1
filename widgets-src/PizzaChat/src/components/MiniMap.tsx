import { ReactElement, useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// A small delivery map for zone and order cards: Leaflet on Esri's keyless Dark
// Gray Canvas tiles, as the DeliveryMap widget and ako/ChatV2's map cards. The
// coordinates come from the app (rest/pizzachat/v1), never from the model.

const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas";
const ATTRIBUTION = 'Tiles &copy; <a href="https://www.esri.com" target="_blank" rel="noopener">Esri</a>, &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>';

type LatLon = [number, number];
const ok = (lat: number, lon: number): LatLon | undefined => (Number.isFinite(lat) && Number.isFinite(lon) && !(lat === 0 && lon === 0) ? [lat, lon] : undefined);

function pin(kind: string, icon: string, label: string): L.DivIcon {
    const html = document.createElement("div");
    html.className = "pc-pin-inner";
    const mk = document.createElement("span");
    mk.className = "pc-mk";
    const ms = document.createElement("span");
    ms.className = "ms";
    ms.setAttribute("aria-hidden", "true");
    ms.textContent = icon;
    mk.append(ms);
    html.append(mk);
    if (label) {
        const nm = document.createElement("span");
        nm.className = "pc-nm";
        nm.textContent = label;
        html.append(nm);
    }
    return L.divIcon({ className: `pc-pin pc-pin--${kind}`, html, iconSize: [28, 28], iconAnchor: [14, 14] });
}

export interface MiniMapProps { store: [number, number]; dest?: [number, number]; destLabel?: string; distance?: string; courier?: number; height?: number }

export function MiniMap({ store, dest, destLabel, distance, courier, height = 180 }: MiniMapProps): ReactElement {
    const box = useRef<HTMLDivElement>(null);
    const [offline, setOffline] = useState(false);
    useEffect(() => {
        const el = box.current;
        const s = ok(store[0], store[1]);
        if (!el || !s) return;
        const d = dest ? ok(dest[0], dest[1]) : undefined;
        const lmap = L.map(el, { scrollWheelZoom: false, zoomControl: false, attributionControl: true, dragging: true, center: s, zoom: 14 });
        let loaded = 0;
        let failed = 0;
        const base = L.tileLayer(`${ESRI}/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`, { maxZoom: 16, attribution: ATTRIBUTION });
        base.on("tileload", () => { loaded++; });
        base.on("tileerror", () => { failed++; if (!loaded && failed >= 2) setOffline(true); });
        base.addTo(lmap);
        L.tileLayer(`${ESRI}/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}`, { maxZoom: 16 }).addTo(lmap);
        const accent = getComputedStyle(el).getPropertyValue("--primary").trim() || "#ff9d00";
        L.marker(s, { icon: pin("store", "local_pizza", "MISSION_KITCHEN"), title: "Store", keyboard: false }).addTo(lmap);
        if (d) {
            const route = L.polyline([s, d], { color: accent, weight: 3, opacity: 0.9, dashArray: "6 6" }).addTo(lmap);
            if (distance) route.bindTooltip(distance, { permanent: true, direction: "right", offset: [12, 0], className: "pc-distance" });
            L.marker(d, { icon: pin("dest", "location_on", destLabel ?? ""), title: destLabel || "Destination", keyboard: false }).addTo(lmap);
            if (courier !== undefined && courier >= 0) {
                const t = Math.min(1, Math.max(0, courier));
                L.marker([s[0] + (d[0] - s[0]) * t, s[1] + (d[1] - s[1]) * t], { icon: pin("courier", "electric_moped", ""), title: "Courier", zIndexOffset: 1000, keyboard: false }).addTo(lmap);
            }
        }
        const fit = (): void => {
            lmap.invalidateSize();
            if (d) lmap.fitBounds(L.latLngBounds([s, d]), { padding: [36, 36], maxZoom: 15, animate: false });
            else lmap.setView(s, 14, { animate: false });
        };
        fit();
        const ro = new ResizeObserver(fit);
        ro.observe(el);
        return () => { ro.disconnect(); lmap.remove(); };
    }, [store[0], store[1], dest?.[0], dest?.[1], destLabel, distance, courier]);
    return (
        <div className={`pc-map${offline ? " pc-map--offline" : ""}`}>
            <div ref={box} className="pc-map-box" style={{ height }} role="img" aria-label={dest ? `Map: store to ${destLabel || "destination"}${distance ? ", " + distance : ""}` : "Map: the store"} />
        </div>
    );
}
